# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class CashExpenseSettlementWizard(models.TransientModel):
    _name = 'cash.expense.settlement.wizard'
    _description = 'Assistant de Règlement d\'Avance'

    expense_id = fields.Many2one(
        'cash.expense',
        string='Avance',
        required=True,
        readonly=True
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employé',
        related='expense_id.employee_id',
        readonly=True
    )

    amount_advanced = fields.Monetary(
        string='Montant de l\'avance',
        related='expense_id.amount',
        readonly=True,
        currency_field='currency_id'
    )

    # Lignes de dépenses détaillées (optionnelles)
    line_ids = fields.One2many(
        'cash.expense.settlement.line',
        'wizard_id',
        string='Détail des dépenses',
        help="Détaillez les dépenses effectuées (optionnel). Si renseigné, le montant sera calculé automatiquement."
    )

    # Mode de saisie
    use_lines = fields.Boolean(
        string='Détailler les dépenses',
        default=False,
        help="Cochez pour saisir le détail des dépenses ligne par ligne"
    )

    amount_from_lines = fields.Monetary(
        string='Total des lignes',
        compute='_compute_amount_from_lines',
        currency_field='currency_id',
        help="Somme calculée depuis les lignes de dépense"
    )

    amount_spent = fields.Monetary(
        string='Montant dépensé',
        currency_field='currency_id',
        help="Montant réellement dépensé par l'employé"
    )

    amount_to_return = fields.Monetary(
        string='Montant à rendre',
        compute='_compute_amounts',
        currency_field='currency_id',
        help="Montant que l'employé doit rendre à la caisse"
    )

    amount_to_pay = fields.Monetary(
        string='Montant à payer',
        compute='_compute_amounts',
        currency_field='currency_id',
        help="Montant supplémentaire à payer à l'employé si les dépenses dépassent l'avance"
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='expense_id.currency_id',
        readonly=True
    )

    cash_id = fields.Many2one(
        'treasury.cash',
        string='Caisse',
        related='expense_id.cash_id',
        readonly=True
    )

    notes = fields.Text(
        string='Notes'
    )

    # Justificatifs du règlement (globaux)
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'settlement_wizard_attachment_rel',
        'wizard_id',
        'attachment_id',
        string='Justificatifs généraux',
        help="Justificatifs globaux (ou utilisez les justificatifs par ligne)"
    )

    settlement_type = fields.Selection([
        ('return', 'Retour d\'argent'),
        ('exact', 'Montant exact'),
        ('additional', 'Paiement supplémentaire')
    ], string='Type de règlement', compute='_compute_amounts')

    @api.depends('line_ids.amount')
    def _compute_amount_from_lines(self):
        """Calculer le total depuis les lignes"""
        for wizard in self:
            wizard.amount_from_lines = sum(wizard.line_ids.mapped('amount'))

    @api.onchange('use_lines', 'line_ids', 'amount_from_lines')
    def _onchange_lines(self):
        """Mettre à jour le montant dépensé depuis les lignes"""
        if self.use_lines:
            self.amount_spent = self.amount_from_lines

    @api.depends('amount_advanced', 'amount_spent')
    def _compute_amounts(self):
        """Calculer les montants à rendre/payer et le type de règlement"""
        for wizard in self:
            if wizard.amount_spent < wizard.amount_advanced:
                wizard.amount_to_return = wizard.amount_advanced - wizard.amount_spent
                wizard.amount_to_pay = 0.0
                wizard.settlement_type = 'return'
            elif wizard.amount_spent > wizard.amount_advanced:
                wizard.amount_to_return = 0.0
                wizard.amount_to_pay = wizard.amount_spent - wizard.amount_advanced
                wizard.settlement_type = 'additional'
            else:
                wizard.amount_to_return = 0.0
                wizard.amount_to_pay = 0.0
                wizard.settlement_type = 'exact'

    @api.constrains('amount_spent')
    def _check_amount_spent(self):
        """Vérifier que le montant dépensé est positif"""
        for wizard in self:
            if wizard.amount_spent < 0:
                raise ValidationError(_("Le montant dépensé ne peut pas être négatif !"))


    def action_settle(self):
        """Régler l'avance"""
        self.ensure_one()

        # Si mode lignes activé, synchroniser le montant depuis les lignes
        if self.use_lines and self.line_ids:
            total_lines = sum(self.line_ids.mapped('amount'))
            self.amount_spent = total_lines

        # Vérifier les justificatifs (globaux ou par ligne)
        has_global_attachments = bool(self.attachment_ids)
        has_line_attachments = any(line.attachment_ids for line in self.line_ids)

        if not has_global_attachments and not has_line_attachments:
            raise ValidationError(_(
                "Veuillez joindre au moins un justificatif de dépense "
                "(soit dans les justificatifs généraux, soit sur les lignes de dépense) !"
            ))

        # Vérifier le montant dépensé
        if self.amount_spent <= 0:
            raise ValidationError(_("Veuillez saisir le montant dépensé !"))

        # Si des lignes sont utilisées, les créer sur l'avance originale
        if self.use_lines and self.line_ids:
            for line in self.line_ids:
                # Créer la ligne de dépense sur l'avance
                expense_line = self.env['cash.expense.line'].create({
                    'expense_id': self.expense_id.id,
                    'name': line.name + (' - ' + line.description if line.description else ''),
                    'quantity': 1,
                    'unit_price': line.amount,
                })
                # Attacher les justificatifs de la ligne
                for attachment in line.attachment_ids:
                    attachment.write({
                        'res_model': 'cash.expense.line',
                        'res_id': expense_line.id
                    })

        # Mettre à jour l'avance
        self.expense_id.write({
            'amount_spent': self.amount_spent,
            'state': 'settled',
            'settled_by': self.env.user.id,
            'settled_date': fields.Datetime.now()
        })

        # Attacher les justificatifs globaux à l'avance
        for attachment in self.attachment_ids:
            attachment.write({
                'res_model': 'cash.expense',
                'res_id': self.expense_id.id
            })

        # Créer une opération de caisse si besoin
        operation_type = False
        operation_amount = 0.0
        operation_desc = ""

        if self.amount_to_return > 0:
            # L'employé rend de l'argent : entrée de caisse
            operation_type = 'in'
            operation_amount = self.amount_to_return
            operation_desc = _("Retour d'argent - Avance %s - %s") % (
                self.expense_id.name, self.employee_id.name
            )

        elif self.amount_to_pay > 0:
            # On doit payer un supplément : sortie de caisse
            operation_type = 'out'
            operation_amount = self.amount_to_pay
            operation_desc = _("Paiement supplémentaire - Avance %s - %s") % (
                self.expense_id.name, self.employee_id.name
            )

        if operation_type:
            # Chercher la catégorie appropriée
            if operation_type == 'in':
                category = self.env.ref('adi_cash_expense.category_advance_return', raise_if_not_found=False)
            else:
                category = self.env.ref('adi_cash_expense.category_additional_payment', raise_if_not_found=False)

            if not category:
                category = self.env['treasury.operation.category'].search([
                    ('operation_type', 'in', [operation_type, 'both'])
                ], limit=1)

            # Créer l'opération
            operation_vals = {
                'cash_id': self.cash_id.id,
                'operation_type': operation_type,
                'category_id': category.id if category else False,
                'amount': operation_amount,
                'date': fields.Datetime.now(),
                'description': operation_desc,
                'reference': self.expense_id.name,
                'partner_id': self.expense_id.partner_id.id if self.expense_id.partner_id else False,
                'observations': self.notes or '',
                'is_manual': True,
                'state': 'draft',
            }

            operation = self.env['treasury.cash.operation'].create(operation_vals)
            operation.action_post()

            # Message dans le chatter de l'avance
            self.expense_id.message_post(
                body=_("Règlement effectué - Opération de caisse : %s") % operation.name
            )

        else:
            # Montant exact, pas d'opération supplémentaire
            self.expense_id.message_post(
                body=_("Règlement effectué - Montant exact dépensé")
            )

        # Message de succès
        message = ""
        if self.settlement_type == 'return':
            message = _("L'avance a été réglée. L'employé a rendu %s %s.") % (
                self.amount_to_return, self.currency_id.symbol
            )
        elif self.settlement_type == 'additional':
            message = _("L'avance a été réglée. Un paiement supplémentaire de %s %s a été effectué.") % (
                self.amount_to_pay, self.currency_id.symbol
            )
        else:
            message = _("L'avance a été réglée. Le montant exact a été dépensé.")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Règlement effectué'),
                'message': message,
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close'
                }
            }
        }


class CashExpenseSettlementLine(models.TransientModel):
    _name = 'cash.expense.settlement.line'
    _description = 'Ligne de Règlement d\'Avance'

    wizard_id = fields.Many2one(
        'cash.expense.settlement.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )

    name = fields.Char(
        string='Désignation',
        required=True,
        help="Description de la dépense"
    )

    description = fields.Text(
        string='Détails',
        help="Détails supplémentaires sur la dépense"
    )

    amount = fields.Monetary(
        string='Montant',
        required=True,
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='wizard_id.currency_id',
        readonly=True
    )

    attachment_ids = fields.Many2many(
        'ir.attachment',
        'settlement_line_attachment_rel',
        'line_id',
        'attachment_id',
        string='Justificatif',
        help="Facture ou reçu pour cette dépense"
    )

    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        help="Date de la dépense"
    )
