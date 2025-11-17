# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PersonalCashAccount(models.Model):
    _name = 'personal.cash.account'
    _description = 'Compte Personnel de Caisse'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employé',
        required=True,
        ondelete='restrict',
        tracking=True
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Partenaire',
        related='employee_id.address_home_id',
        store=True
    )

    # Soldes
    current_balance = fields.Monetary(
        string='Solde actuel',
        currency_field='currency_id',
        compute='_compute_current_balance',
        store=True,
        help="Solde actuel des avances en cours (montant donné - montant dépensé)"
    )

    advance_limit = fields.Monetary(
        string='Limite d\'avance',
        currency_field='currency_id',
        default=0.0,
        tracking=True,
        help="Montant maximum d'avance autorisé pour cet employé (0 = pas de limite)"
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    # Relations
    expense_ids = fields.One2many(
        'cash.expense',
        'personal_account_id',
        string='Dépenses'
    )

    advance_ids = fields.One2many(
        'cash.expense',
        'personal_account_id',
        string='Avances',
        domain=[('expense_type', '=', 'advance')]
    )

    # Statistiques
    total_expenses = fields.Monetary(
        string='Total dépenses',
        currency_field='currency_id',
        compute='_compute_statistics'
    )

    total_advances = fields.Monetary(
        string='Total avances reçues',
        currency_field='currency_id',
        compute='_compute_statistics'
    )

    total_reimbursements = fields.Monetary(
        string='Total remboursements',
        currency_field='currency_id',
        compute='_compute_statistics'
    )

    expense_count = fields.Integer(
        string='Nombre de dépenses',
        compute='_compute_statistics'
    )

    active_advance_count = fields.Integer(
        string='Avances en cours',
        compute='_compute_statistics',
        help="Nombre d'avances payées mais non encore réglées"
    )

    # Autres
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )

    active = fields.Boolean(
        string='Actif',
        default=True
    )

    notes = fields.Text(
        string='Notes'
    )

    @api.depends('advance_ids.state', 'advance_ids.amount', 'advance_ids.amount_remaining')
    def _compute_current_balance(self):
        """Calculer le solde actuel des avances en cours"""
        for account in self:
            # Somme des montants restants des avances payées mais non réglées
            active_advances = account.advance_ids.filtered(
                lambda a: a.state == 'paid'
            )
            account.current_balance = sum(active_advances.mapped('amount_remaining'))

    def _compute_statistics(self):
        """Calculer les statistiques"""
        for account in self:
            all_expenses = account.expense_ids.filtered(
                lambda e: e.state in ['approved', 'paid', 'settled']
            )

            account.expense_count = len(all_expenses)

            # Avances
            advances = all_expenses.filtered(lambda e: e.expense_type == 'advance')
            account.total_advances = sum(advances.mapped('amount'))
            account.active_advance_count = len(advances.filtered(lambda a: a.state == 'paid'))

            # Remboursements
            reimbursements = all_expenses.filtered(lambda e: e.expense_type == 'reimbursement')
            account.total_reimbursements = sum(reimbursements.mapped('amount'))

            # Total
            account.total_expenses = account.total_advances + account.total_reimbursements

    @api.constrains('employee_id')
    def _check_employee_unique(self):
        """Vérifier qu'un employé n'a qu'un seul compte personnel"""
        for account in self:
            existing = self.search([
                ('employee_id', '=', account.employee_id.id),
                ('id', '!=', account.id),
                ('company_id', '=', account.company_id.id)
            ])
            if existing:
                raise ValidationError(_(
                    "L'employé %s a déjà un compte personnel !"
                ) % account.employee_id.name)

    @api.constrains('advance_limit')
    def _check_advance_limit(self):
        """Vérifier que la limite est positive"""
        for account in self:
            if account.advance_limit < 0:
                raise ValidationError(_("La limite d'avance ne peut pas être négative !"))

    def action_view_expenses(self):
        """Afficher toutes les dépenses de ce compte"""
        self.ensure_one()

        return {
            'name': _('Dépenses de %s') % self.employee_id.name,
            'type': 'ir.actions.act_window',
            'res_model': 'cash.expense',
            'view_mode': 'tree,form',
            'domain': [('personal_account_id', '=', self.id)],
            'context': {
                'default_employee_id': self.employee_id.id,
                'default_personal_account_id': self.id,
            }
        }

    def action_view_advances(self):
        """Afficher les avances en cours"""
        self.ensure_one()

        return {
            'name': _('Avances de %s') % self.employee_id.name,
            'type': 'ir.actions.act_window',
            'res_model': 'cash.expense',
            'view_mode': 'tree,form',
            'domain': [
                ('personal_account_id', '=', self.id),
                ('expense_type', '=', 'advance'),
                ('state', '=', 'paid')
            ],
            'context': {
                'default_employee_id': self.employee_id.id,
                'default_personal_account_id': self.id,
                'default_expense_type': 'advance',
            }
        }

    def name_get(self):
        """Affichage personnalisé"""
        result = []
        for account in self:
            name = _("Compte de %s") % account.employee_id.name
            if account.current_balance > 0:
                name += _(" (Solde: %s %s)") % (account.current_balance, account.currency_id.symbol)
            result.append((account.id, name))
        return result
