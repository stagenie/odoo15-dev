# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class TreasuryBank(models.Model):
    _name = 'treasury.bank'
    _description = 'Compte Bancaire de Trésorerie'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # Identification
    name = fields.Char(
        string='Nom du compte',
        required=True,
        tracking=True
    )
    code = fields.Char(
        string='Code',
        required=True,
        tracking=True
    )
    active = fields.Boolean(
        string='Actif',
        default=True,
        tracking=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        required=True,
        default=lambda self: self.env.company.currency_id,
        tracking=True
    )

    # Informations bancaires
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal Bancaire',
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]",
        required=True,
        tracking=True,
        help="Journal comptable de type banque associé à ce compte"
    )
    bank_id = fields.Many2one(
        'res.bank',
        string='Banque',
        tracking=True
    )
    account_number = fields.Char(
        string='Numéro de compte',
        tracking=True
    )
    iban = fields.Char(
        string='IBAN',
        tracking=True
    )
    bic = fields.Char(
        string='BIC/SWIFT',
        tracking=True
    )
    bank_name = fields.Char(
        string='Nom de la banque',
        related='bank_id.name',
        store=True,
        readonly=True
    )
    branch = fields.Char(
        string='Agence',
        tracking=True
    )

    # Responsabilité
    responsible_id = fields.Many2one(
        'res.users',
        string='Responsable principal',
        default=lambda self: self.env.user,
        tracking=True
    )
    user_ids = fields.Many2many(
        'res.users',
        'treasury_bank_user_rel',
        'bank_id',
        'user_id',
        string='Utilisateurs autorisés',
        help="Utilisateurs ayant accès à ce compte bancaire"
    )

    # Soldes
    current_balance = fields.Monetary(
        string='Solde Actuel (Comptable)',
        compute='_compute_current_balance',
        store=True,
        currency_field='currency_id',
        help="Solde calculé à partir des opérations comptabilisées (basé sur date d'opération)"
    )
    available_balance = fields.Monetary(
        string='Solde Disponible',
        compute='_compute_available_balance',
        store=True,
        currency_field='currency_id',
        help="Solde calculé à partir des opérations avec date de valeur passée"
    )
    last_closing_date = fields.Date(
        string='Date dernière clôture',
        readonly=True,
        tracking=True
    )
    last_closing_balance = fields.Monetary(
        string='Solde dernière clôture',
        readonly=True,
        currency_field='currency_id'
    )
    last_statement_date = fields.Date(
        string='Date dernier relevé',
        tracking=True
    )
    last_statement_balance = fields.Monetary(
        string='Solde dernier relevé',
        currency_field='currency_id',
        tracking=True
    )

    # Configuration
    overdraft_limit = fields.Monetary(
        string='Découvert autorisé',
        default=0.0,
        currency_field='currency_id',
        tracking=True,
        help="Montant du découvert autorisé (positif). 0 = pas de découvert"
    )
    state = fields.Selection([
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
        ('closed', 'Fermé')
    ], string='État', default='active', required=True, tracking=True)

    # Relations
    operation_ids = fields.One2many(
        'treasury.bank.operation',
        'bank_id',
        string='Opérations'
    )
    closing_ids = fields.One2many(
        'treasury.bank.closing',
        'bank_id',
        string='Clôtures/Rapprochements'
    )
    transfer_in_ids = fields.One2many(
        'treasury.transfer',
        'bank_to_id',
        string='Transferts entrants'
    )
    transfer_out_ids = fields.One2many(
        'treasury.transfer',
        'bank_from_id',
        string='Transferts sortants'
    )

    # Compteurs
    operation_count = fields.Integer(
        string='Nombre d\'opérations',
        compute='_compute_counts'
    )
    closing_count = fields.Integer(
        string='Nombre de clôtures',
        compute='_compute_counts'
    )
    transfer_count = fields.Integer(
        string='Nombre de transferts',
        compute='_compute_counts'
    )

    _sql_constraints = [
        ('code_company_unique', 'unique(code, company_id)',
         'Le code du compte bancaire doit être unique par société !'),
        ('journal_company_unique', 'unique(journal_id, company_id)',
         'Un journal bancaire ne peut être associé qu\'à un seul compte bancaire !'),
        ('overdraft_positive', 'check(overdraft_limit >= 0)',
         'Le découvert autorisé doit être positif ou nul !')
    ]

    @api.depends('operation_ids', 'operation_ids.state', 'operation_ids.amount',
                 'operation_ids.operation_type', 'closing_ids.state',
                 'closing_ids.balance_end_bank')
    def _compute_current_balance(self):
        """Calcule le solde actuel du compte bancaire (basé sur date d'opération)"""
        for bank in self:
            # Chercher la dernière clôture validée
            last_closing = self.env['treasury.bank.closing'].search([
                ('bank_id', '=', bank.id),
                ('state', '=', 'validated')
            ], order='closing_date desc, id desc', limit=1)

            if last_closing:
                # Partir du solde de la dernière clôture
                balance = last_closing.balance_end_bank

                # Ajouter les opérations postérieures à la clôture
                # qui ne sont pas déjà dans une clôture validée
                operations = self.env['treasury.bank.operation'].search([
                    ('bank_id', '=', bank.id),
                    ('state', '=', 'posted'),
                    ('date', '>', last_closing.closing_date),
                    '|',
                    ('closing_id', '=', False),
                    ('closing_id.state', '!=', 'validated')
                ])
            else:
                # Pas de clôture validée : calculer depuis toutes les opérations
                balance = 0.0
                operations = self.env['treasury.bank.operation'].search([
                    ('bank_id', '=', bank.id),
                    ('state', '=', 'posted')
                ])

            # Calculer le solde
            for op in operations:
                if op.operation_type == 'in':
                    balance += op.amount
                else:
                    balance -= op.amount

            bank.current_balance = balance

    @api.depends('operation_ids', 'operation_ids.state', 'operation_ids.amount',
                 'operation_ids.operation_type', 'operation_ids.value_date')
    def _compute_available_balance(self):
        """Calcule le solde disponible (basé sur date de valeur)"""
        for bank in self:
            today = fields.Date.context_today(self)

            # Chercher la dernière clôture validée
            last_closing = self.env['treasury.bank.closing'].search([
                ('bank_id', '=', bank.id),
                ('state', '=', 'validated')
            ], order='closing_date desc, id desc', limit=1)

            if last_closing:
                balance = last_closing.balance_end_bank

                # Opérations avec value_date > closing_date et <= today
                operations = self.env['treasury.bank.operation'].search([
                    ('bank_id', '=', bank.id),
                    ('state', '=', 'posted'),
                    ('value_date', '>', last_closing.closing_date),
                    ('value_date', '<=', today),
                    '|',
                    ('closing_id', '=', False),
                    ('closing_id.state', '!=', 'validated')
                ])
            else:
                balance = 0.0
                operations = self.env['treasury.bank.operation'].search([
                    ('bank_id', '=', bank.id),
                    ('state', '=', 'posted'),
                    ('value_date', '<=', today)
                ])

            # Calculer le solde disponible
            for op in operations:
                if op.operation_type == 'in':
                    balance += op.amount
                else:
                    balance -= op.amount

            bank.available_balance = balance

    @api.depends('operation_ids', 'closing_ids', 'transfer_in_ids', 'transfer_out_ids')
    def _compute_counts(self):
        """Calcule les compteurs pour les smart buttons"""
        for bank in self:
            bank.operation_count = len(bank.operation_ids)
            bank.closing_count = len(bank.closing_ids)
            bank.transfer_count = len(bank.transfer_in_ids) + len(bank.transfer_out_ids)

    @api.constrains('journal_id')
    def _check_journal_type(self):
        """Vérifie que le journal est bien de type 'bank'"""
        for bank in self:
            if bank.journal_id and bank.journal_id.type != 'bank':
                raise ValidationError(_(
                    "Le journal '%s' n'est pas de type 'Banque'. "
                    "Veuillez sélectionner un journal bancaire."
                ) % bank.journal_id.name)

    @api.constrains('state')
    def _check_state_change(self):
        """Vérifie les changements d'état"""
        for bank in self:
            if bank.state == 'closed':
                # Vérifier qu'il n'y a pas d'opérations en brouillon
                draft_ops = self.env['treasury.bank.operation'].search_count([
                    ('bank_id', '=', bank.id),
                    ('state', '=', 'draft')
                ])
                if draft_ops > 0:
                    raise ValidationError(_(
                        "Impossible de fermer le compte bancaire : "
                        "il contient %d opération(s) en brouillon."
                    ) % draft_ops)

    def action_view_operations(self):
        """Ouvre la vue des opérations du compte"""
        self.ensure_one()
        return {
            'name': _('Opérations - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.bank.operation',
            'view_mode': 'tree,form,kanban',
            'domain': [('bank_id', '=', self.id)],
            'context': {
                'default_bank_id': self.id,
                'search_default_group_by_date': 1,
            }
        }

    def action_view_closings(self):
        """Ouvre la vue des clôtures du compte"""
        self.ensure_one()
        return {
            'name': _('Rapprochements - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.bank.closing',
            'view_mode': 'tree,form,kanban',
            'domain': [('bank_id', '=', self.id)],
            'context': {
                'default_bank_id': self.id,
            }
        }

    def action_view_transfers(self):
        """Ouvre la vue des transferts du compte"""
        self.ensure_one()
        return {
            'name': _('Transferts - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.transfer',
            'view_mode': 'tree,form,kanban',
            'domain': ['|', ('bank_from_id', '=', self.id), ('bank_to_id', '=', self.id)],
            'context': {
                'default_bank_from_id': self.id,
            }
        }

    def action_create_operation(self):
        """Crée une nouvelle opération bancaire"""
        self.ensure_one()
        return {
            'name': _('Nouvelle opération - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.bank.operation',
            'view_mode': 'form',
            'context': {
                'default_bank_id': self.id,
            },
            'target': 'new',
        }

    def action_create_closing(self):
        """Crée un nouveau rapprochement bancaire"""
        self.ensure_one()

        # Vérifier qu'il n'y a pas déjà une clôture en cours
        existing_closing = self.env['treasury.bank.closing'].search([
            ('bank_id', '=', self.id),
            ('state', 'in', ['draft', 'confirmed'])
        ], limit=1)

        if existing_closing:
            raise UserError(_(
                "Un rapprochement est déjà en cours pour ce compte bancaire.\n"
                "Veuillez le terminer avant d'en créer un nouveau.\n"
                "Référence: %s"
            ) % existing_closing.name)

        return {
            'name': _('Nouveau rapprochement - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.bank.closing',
            'view_mode': 'form',
            'context': {
                'default_bank_id': self.id,
            },
            'target': 'current',
        }

    def action_view_journal(self):
        """Ouvre le journal comptable associé"""
        self.ensure_one()
        return {
            'name': _('Journal - %s') % self.journal_id.name,
            'type': 'ir.actions.act_window',
            'res_model': 'account.journal',
            'view_mode': 'form',
            'res_id': self.journal_id.id,
            'target': 'current',
        }

    def name_get(self):
        """Format d'affichage du nom"""
        result = []
        for bank in self:
            name = f"[{bank.code}] {bank.name}"
            if bank.account_number:
                name += f" ({bank.account_number})"
            result.append((bank.id, name))
        return result
