# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class CashExpense(models.Model):
    _name = 'cash.expense'
    _description = 'Dépense de Caisse'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'
    _rec_name = 'name'

    # Champs de base
    name = fields.Char(
        string='Référence',
        required=True,
        readonly=True,
        default=lambda self: _('Nouveau'),
        copy=False
    )

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
        tracking=True,
        states={'paid': [('readonly', True)], 'settled': [('readonly', True)], 'cancel': [('readonly', True)]}
    )

    # Type de dépense
    expense_type = fields.Selection([
        ('reimbursement', 'Remboursement'),
        ('advance', 'Avance')
    ], string='Type de dépense', required=True, default='reimbursement', tracking=True,
        states={'paid': [('readonly', True)], 'settled': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Remboursement : la personne a déjà payé et doit être remboursée\n"
             "Avance : on donne le montant à la personne à l'avance")

    # Bénéficiaire (obligatoire)
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employé bénéficiaire',
        required=True,
        tracking=True,
        states={'paid': [('readonly', True)], 'settled': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Personne qui reçoit le remboursement ou l'avance"
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Partenaire',
        related='employee_id.address_home_id',
        store=True,
        help="Partenaire lié à l'employé"
    )

    # Structure (optionnel mais avec personne obligatoire)
    department_id = fields.Many2one(
        'hr.department',
        string='Département',
        tracking=True,
        states={'paid': [('readonly', True)], 'settled': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Département ou structure concerné par la dépense"
    )

    # Montants
    amount = fields.Monetary(
        string='Montant total',
        required=True,
        currency_field='currency_id',
        tracking=True,
        compute='_compute_amount',
        store=True,
        readonly=False
    )

    amount_spent = fields.Monetary(
        string='Montant dépensé',
        currency_field='currency_id',
        help="Montant réellement dépensé (pour les avances)"
    )

    amount_remaining = fields.Monetary(
        string='Solde restant',
        currency_field='currency_id',
        compute='_compute_remaining',
        store=True,
        help="Montant restant à rendre (pour les avances)"
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    # Description et justifications
    description = fields.Text(
        string='Description',
        required=True,
        states={'paid': [('readonly', True)], 'settled': [('readonly', True)], 'cancel': [('readonly', True)]}
    )

    notes = fields.Text(
        string='Notes internes'
    )

    # Lignes de dépenses
    line_ids = fields.One2many(
        'cash.expense.line',
        'expense_id',
        string='Lignes de dépense',
        states={'paid': [('readonly', True)], 'settled': [('readonly', True)], 'cancel': [('readonly', True)]}
    )

    # Pièces jointes (justificatifs)
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'cash_expense_attachment_rel',
        'expense_id',
        'attachment_id',
        string='Justificatifs',
        help="Factures, reçus, bons de commande, etc."
    )

    attachment_count = fields.Integer(
        compute='_compute_attachment_count',
        string='Nombre de pièces jointes'
    )

    # Lien avec la trésorerie
    cash_id = fields.Many2one(
        'treasury.cash',
        string='Caisse',
        required=True,
        domain="[('state', '=', 'open')]",
        tracking=True,
        states={'paid': [('readonly', True)], 'settled': [('readonly', True)], 'cancel': [('readonly', True)]}
    )

    # Compte personnel
    personal_account_id = fields.Many2one(
        'personal.cash.account',
        string='Compte personnel',
        compute='_compute_personal_account',
        store=True
    )

    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('submitted', 'Soumis'),
        ('approved', 'Approuvé'),
        ('paid', 'Payé'),
        ('settled', 'Réglé'),
        ('cancel', 'Annulé')
    ], string='État', default='draft', tracking=True, required=True)

    # Approbation
    approved_by = fields.Many2one(
        'res.users',
        string='Approuvé par',
        readonly=True,
        tracking=True
    )

    approved_date = fields.Datetime(
        string='Date d\'approbation',
        readonly=True
    )

    # Paiement
    paid_by = fields.Many2one(
        'res.users',
        string='Payé par',
        readonly=True,
        tracking=True
    )

    paid_date = fields.Datetime(
        string='Date de paiement',
        readonly=True
    )

    # Règlement (pour les avances)
    settled_by = fields.Many2one(
        'res.users',
        string='Réglé par',
        readonly=True,
        tracking=True
    )

    settled_date = fields.Datetime(
        string='Date de règlement',
        readonly=True
    )

    # Autres
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )

    user_id = fields.Many2one(
        'res.users',
        string='Créé par',
        default=lambda self: self.env.user,
        readonly=True
    )

    @api.depends('line_ids.total_amount')
    def _compute_amount(self):
        """Calculer le montant total depuis les lignes"""
        for expense in self:
            expense.amount = sum(expense.line_ids.mapped('total_amount'))

    @api.depends('amount', 'amount_spent', 'expense_type')
    def _compute_remaining(self):
        """Calculer le solde restant pour les avances"""
        for expense in self:
            if expense.expense_type == 'advance':
                expense.amount_remaining = expense.amount - expense.amount_spent
            else:
                expense.amount_remaining = 0.0

    @api.depends('employee_id')
    def _compute_personal_account(self):
        """Récupérer ou créer le compte personnel de l'employé"""
        for expense in self:
            if expense.employee_id:
                account = self.env['personal.cash.account'].search([
                    ('employee_id', '=', expense.employee_id.id)
                ], limit=1)

                if not account:
                    account = self.env['personal.cash.account'].create({
                        'employee_id': expense.employee_id.id,
                    })

                expense.personal_account_id = account
            else:
                expense.personal_account_id = False

    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        """Compter les pièces jointes"""
        for expense in self:
            expense.attachment_count = len(expense.attachment_ids)

    @api.model_create_multi
    def create(self, vals_list):
        """Générer la référence à la création"""
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('cash.expense') or _('Nouveau')

        return super().create(vals_list)

    @api.constrains('amount')
    def _check_amount(self):
        """Vérifier que le montant est positif"""
        for expense in self:
            if expense.amount <= 0:
                raise ValidationError(_("Le montant doit être positif !"))

    @api.constrains('expense_type', 'attachment_ids')
    def _check_justifications(self):
        """Vérifier que les remboursements ont des justificatifs"""
        for expense in self:
            if expense.expense_type == 'reimbursement' and expense.state in ['submitted', 'approved', 'paid']:
                if not expense.attachment_ids and not expense.line_ids.mapped('attachment_ids'):
                    raise ValidationError(_(
                        "Les remboursements doivent avoir au moins un justificatif !"
                    ))

    def action_submit(self):
        """Soumettre la dépense pour approbation"""
        for expense in self:
            if expense.state != 'draft':
                raise UserError(_("Seules les dépenses en brouillon peuvent être soumises."))

            if not expense.line_ids:
                raise UserError(_("Veuillez ajouter au moins une ligne de dépense."))

            expense.state = 'submitted'
            expense.message_post(body=_("Dépense soumise pour approbation"))

    def action_approve(self):
        """Approuver la dépense"""
        for expense in self:
            if expense.state != 'submitted':
                raise UserError(_("Seules les dépenses soumises peuvent être approuvées."))

            # Vérifier la limite d'avance pour les avances
            if expense.expense_type == 'advance':
                if expense.personal_account_id.advance_limit > 0:
                    new_balance = expense.personal_account_id.current_balance + expense.amount
                    if new_balance > expense.personal_account_id.advance_limit:
                        raise UserError(_(
                            "Cette avance dépasse la limite autorisée pour %s.\n"
                            "Solde actuel : %s %s\n"
                            "Limite : %s %s\n"
                            "Nouveau solde : %s %s"
                        ) % (
                            expense.employee_id.name,
                            expense.personal_account_id.current_balance,
                            expense.currency_id.symbol,
                            expense.personal_account_id.advance_limit,
                            expense.currency_id.symbol,
                            new_balance,
                            expense.currency_id.symbol
                        ))

            expense.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
                'approved_date': fields.Datetime.now()
            })
            expense.message_post(body=_("Dépense approuvée par %s") % self.env.user.name)

    def action_pay(self):
        """Payer la dépense (créer l'opération de caisse)"""
        for expense in self:
            if expense.state != 'approved':
                raise UserError(_("Seules les dépenses approuvées peuvent être payées."))

            # Créer l'opération de caisse
            operation_type = 'out'  # Sortie de caisse

            # Chercher la catégorie appropriée
            if expense.expense_type == 'reimbursement':
                category = self.env.ref('adi_cash_expense.category_reimbursement', raise_if_not_found=False)
            else:
                category = self.env.ref('adi_cash_expense.category_advance', raise_if_not_found=False)

            if not category:
                category = self.env['treasury.operation.category'].search([
                    ('operation_type', 'in', ['out', 'both'])
                ], limit=1)

            # Créer l'opération
            operation_vals = {
                'cash_id': expense.cash_id.id,
                'operation_type': operation_type,
                'category_id': category.id if category else False,
                'amount': expense.amount,
                'date': fields.Datetime.now(),
                'description': _("%s - %s - %s") % (
                    dict(expense._fields['expense_type'].selection).get(expense.expense_type),
                    expense.employee_id.name,
                    expense.description
                ),
                'reference': expense.name,
                'partner_id': expense.partner_id.id if expense.partner_id else False,
                'is_manual': True,
                'state': 'draft',
            }

            operation = self.env['treasury.cash.operation'].create(operation_vals)
            operation.action_post()

            # Mettre à jour l'état
            expense.write({
                'state': 'settled' if expense.expense_type == 'reimbursement' else 'paid',
                'paid_by': self.env.user.id,
                'paid_date': fields.Datetime.now()
            })

            expense.message_post(
                body=_("Paiement effectué - Opération de caisse : %s") % operation.name
            )

    def action_settle(self):
        """Régler une avance (ouvrir le wizard de règlement)"""
        self.ensure_one()

        if self.expense_type != 'advance':
            raise UserError(_("Seules les avances peuvent être réglées."))

        if self.state != 'paid':
            raise UserError(_("Seules les avances payées peuvent être réglées."))

        return {
            'name': _('Régler l\'avance'),
            'type': 'ir.actions.act_window',
            'res_model': 'cash.expense.settlement.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_expense_id': self.id,
                'default_amount_spent': self.amount_spent,
            }
        }

    def action_cancel(self):
        """Annuler la dépense"""
        for expense in self:
            if expense.state in ['paid', 'settled']:
                raise UserError(_(
                    "Impossible d'annuler une dépense déjà payée ou réglée."
                ))

            expense.state = 'cancel'
            expense.message_post(body=_("Dépense annulée"))

    def action_draft(self):
        """Remettre en brouillon"""
        for expense in self:
            if expense.state != 'cancel':
                raise UserError(_("Seules les dépenses annulées peuvent être remises en brouillon."))

            expense.state = 'draft'
            expense.message_post(body=_("Dépense remise en brouillon"))

    def action_view_attachments(self):
        """Afficher les pièces jointes"""
        self.ensure_one()

        return {
            'name': _('Justificatifs'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,tree,form',
            'domain': [('id', 'in', self.attachment_ids.ids)],
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
            }
        }

    def action_view_operations(self):
        """Afficher les opérations de caisse liées"""
        self.ensure_one()

        operations = self.env['treasury.cash.operation'].search([
            ('reference', '=', self.name)
        ])

        return {
            'name': _('Opérations de caisse'),
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.cash.operation',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', operations.ids)],
        }

    def action_view_personal_account(self):
        """Afficher le compte personnel"""
        self.ensure_one()

        return {
            'name': _('Compte personnel'),
            'type': 'ir.actions.act_window',
            'res_model': 'personal.cash.account',
            'view_mode': 'form',
            'res_id': self.personal_account_id.id,
        }

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """Récupérer le département de l'employé"""
        if self.employee_id:
            self.department_id = self.employee_id.department_id
