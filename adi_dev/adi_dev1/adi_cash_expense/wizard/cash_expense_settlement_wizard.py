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

    amount_spent = fields.Monetary(
        string='Montant dépensé',
        required=True,
        currency_field='currency_id',
        help="Montant réellement dépensé par l'employé"
    )

    amount_to_return = fields.Monetary(
        string='Montant à rendre',
        compute='_compute_amount_to_return',
        store=True,
        currency_field='currency_id',
        help="Montant que l'employé doit rendre à la caisse"
    )

    amount_to_pay = fields.Monetary(
        string='Montant à payer',
        compute='_compute_amount_to_pay',
        store=True,
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

    # Justificatifs du règlement
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'settlement_wizard_attachment_rel',
        'wizard_id',
        'attachment_id',
        string='Justificatifs de dépenses',
        help="Factures et reçus des dépenses réellement effectuées"
    )

    settlement_type = fields.Selection([
        ('return', 'Retour d\'argent'),
        ('exact', 'Montant exact'),
        ('additional', 'Paiement supplémentaire')
    ], string='Type de règlement', compute='_compute_settlement_type', store=True)

    @api.depends('amount_advanced', 'amount_spent')
    def _compute_amount_to_return(self):
        """Calculer le montant à rendre"""
        for wizard in self:
            if wizard.amount_spent < wizard.amount_advanced:
                wizard.amount_to_return = wizard.amount_advanced - wizard.amount_spent
            else:
                wizard.amount_to_return = 0.0

    @api.depends('amount_advanced', 'amount_spent')
    def _compute_amount_to_pay(self):
        """Calculer le montant supplémentaire à payer"""
        for wizard in self:
            if wizard.amount_spent > wizard.amount_advanced:
                wizard.amount_to_pay = wizard.amount_spent - wizard.amount_advanced
            else:
                wizard.amount_to_pay = 0.0

    @api.depends('amount_to_return', 'amount_to_pay')
    def _compute_settlement_type(self):
        """Déterminer le type de règlement"""
        for wizard in self:
            if wizard.amount_to_return > 0:
                wizard.settlement_type = 'return'
            elif wizard.amount_to_pay > 0:
                wizard.settlement_type = 'additional'
            else:
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

        if not self.attachment_ids:
            raise ValidationError(_(
                "Veuillez joindre au moins un justificatif de dépense !"
            ))

        # Mettre à jour l'avance
        self.expense_id.write({
            'amount_spent': self.amount_spent,
            'state': 'settled',
            'settled_by': self.env.user.id,
            'settled_date': fields.Datetime.now()
        })

        # Attacher les justificatifs à l'avance
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
