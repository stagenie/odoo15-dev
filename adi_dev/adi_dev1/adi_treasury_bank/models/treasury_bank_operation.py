# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class TreasuryBankOperation(models.Model):
    _name = 'treasury.bank.operation'
    _description = 'Opération Bancaire'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    # Identification
    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau'),
        tracking=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
        states={'draft': [('readonly', False)]}
    )

    # Compte bancaire
    bank_id = fields.Many2one(
        'treasury.bank',
        string='Compte bancaire',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        related='bank_id.currency_id',
        store=True,
        readonly=True
    )

    # Type et catégorie
    operation_type = fields.Selection([
        ('in', 'Entrée'),
        ('out', 'Sortie')
    ], string='Type', required=True, readonly=True,
        states={'draft': [('readonly', False)]}, tracking=True)

    category_id = fields.Many2one(
        'treasury.operation.category',
        string='Catégorie',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True
    )

    # Méthode de paiement bancaire
    payment_method = fields.Selection([
        ('transfer', 'Virement'),
        ('check', 'Chèque'),
        ('cash', 'Espèces'),
        ('card', 'Carte Bancaire'),
        ('direct_debit', 'Prélèvement'),
        ('bank_fees', 'Frais Bancaires'),
        ('interest', 'Intérêts'),
        ('other', 'Autre')
    ], string='Méthode de paiement', default='other',
        readonly=True, states={'draft': [('readonly', False)]}, tracking=True)

    # Montant
    amount = fields.Monetary(
        string='Montant',
        required=True,
        currency_field='currency_id',
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True
    )

    # Dates
    date = fields.Datetime(
        string='Date d\'opération',
        required=True,
        default=fields.Datetime.now,
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True,
        help="Date de l'opération comptable"
    )
    value_date = fields.Date(
        string='Date de valeur',
        required=True,
        default=fields.Date.context_today,
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True,
        help="Date à laquelle l'opération est effectivement prise en compte par la banque"
    )

    # Références bancaires
    bank_reference = fields.Char(
        string='Référence bancaire',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Référence fournie par la banque (numéro de virement, etc.)"
    )
    check_number = fields.Char(
        string='Numéro de chèque',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Numéro du chèque si applicable"
    )

    # Partenaire
    partner_id = fields.Many2one(
        'res.partner',
        string='Partenaire',
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True
    )

    # Description
    description = fields.Text(
        string='Description',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('posted', 'Comptabilisé'),
        ('reconciled', 'Rapproché'),
        ('cancel', 'Annulé')
    ], string='État', default='draft', required=True,
        readonly=True, tracking=True)

    # Rapprochement
    is_reconciled = fields.Boolean(
        string='Rapproché',
        default=False,
        help="Indique si l'opération a été rapprochée avec un relevé bancaire"
    )
    reconciliation_date = fields.Date(
        string='Date de rapprochement',
        readonly=True
    )
    closing_id = fields.Many2one(
        'treasury.bank.closing',
        string='Rapprochement bancaire',
        readonly=True,
        ondelete='set null'
    )

    # Relations
    payment_id = fields.Many2one(
        'account.payment',
        string='Paiement comptable',
        readonly=True,
        ondelete='set null',
        help="Paiement Odoo lié à cette opération (si création automatique)"
    )
    transfer_id = fields.Many2one(
        'treasury.transfer',
        string='Transfert',
        readonly=True,
        ondelete='cascade',
        help="Transfert de trésorerie lié à cette opération"
    )

    # Marqueurs
    is_manual = fields.Boolean(
        string='Opération manuelle',
        default=True,
        help="True = saisie manuelle, False = créée automatiquement"
    )
    is_opening = fields.Boolean(
        string='Solde d\'ouverture',
        default=False,
        help="Indique s'il s'agit d'un solde d'ouverture"
    )

    # Champs techniques
    user_id = fields.Many2one(
        'res.users',
        string='Créé par',
        default=lambda self: self.env.user,
        readonly=True
    )

    _sql_constraints = [
        ('amount_positive', 'check(amount > 0)',
         'Le montant doit être strictement positif !')
    ]

    @api.model
    def create(self, vals):
        """Surcharge create pour générer la séquence"""
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'treasury.bank.operation') or _('Nouveau')
        return super(TreasuryBankOperation, self).create(vals)

    @api.constrains('category_id', 'operation_type')
    def _check_category_type(self):
        """Vérifie la cohérence entre la catégorie et le type d'opération"""
        for operation in self:
            if operation.category_id.operation_type == 'in' and operation.operation_type != 'in':
                raise ValidationError(_(
                    "La catégorie '%s' est réservée aux opérations d'entrée."
                ) % operation.category_id.name)
            elif operation.category_id.operation_type == 'out' and operation.operation_type != 'out':
                raise ValidationError(_(
                    "La catégorie '%s' est réservée aux opérations de sortie."
                ) % operation.category_id.name)

    @api.constrains('bank_id', 'state')
    def _check_bank_balance(self):
        """Vérifie que le solde est suffisant pour les sorties"""
        for operation in self:
            if operation.state == 'posted' and operation.operation_type == 'out':
                # Calculer le solde après l'opération
                new_balance = operation.bank_id.current_balance

                # Vérifier le découvert autorisé
                if new_balance < -operation.bank_id.overdraft_limit:
                    raise ValidationError(_(
                        "Solde insuffisant !\n\n"
                        "Solde actuel: %(balance).2f %(currency)s\n"
                        "Découvert autorisé: %(overdraft).2f %(currency)s\n"
                        "Solde après opération: %(new_balance).2f %(currency)s\n\n"
                        "Cette opération dépasserait le découvert autorisé."
                    ) % {
                        'balance': operation.bank_id.current_balance + operation.amount,
                        'currency': operation.currency_id.symbol,
                        'overdraft': operation.bank_id.overdraft_limit,
                        'new_balance': new_balance,
                    })

    @api.onchange('operation_type')
    def _onchange_operation_type(self):
        """Filtre les catégories selon le type d'opération"""
        if self.operation_type:
            return {
                'domain': {
                    'category_id': [
                        ('operation_type', 'in', [self.operation_type, 'both'])
                    ]
                }
            }

    @api.onchange('payment_method')
    def _onchange_payment_method(self):
        """Suggestions selon la méthode de paiement"""
        if self.payment_method == 'bank_fees':
            self.operation_type = 'out'
        elif self.payment_method == 'interest':
            # Les intérêts peuvent être créditeurs ou débiteurs
            pass

    def action_post(self):
        """Comptabilise l'opération"""
        for operation in self:
            if operation.state != 'draft':
                raise UserError(_("Seules les opérations en brouillon peuvent être comptabilisées."))

            # Vérifier que le compte bancaire est actif
            if operation.bank_id.state != 'active':
                raise UserError(_(
                    "Le compte bancaire '%s' n'est pas actif."
                ) % operation.bank_id.name)

            # Mettre à jour l'état
            operation.write({'state': 'posted'})

            # Message dans le chatter
            operation.message_post(
                body=_("Opération comptabilisée : %(type)s de %(amount).2f %(currency)s") % {
                    'type': dict(operation._fields['operation_type'].selection)[operation.operation_type],
                    'amount': operation.amount,
                    'currency': operation.currency_id.symbol,
                }
            )

    def action_cancel(self):
        """Annule l'opération"""
        for operation in self:
            # Vérifier qu'elle n'est pas dans une clôture validée
            if operation.closing_id and operation.closing_id.state == 'validated':
                raise UserError(_(
                    "Impossible d'annuler cette opération : "
                    "elle est incluse dans le rapprochement validé '%s'."
                ) % operation.closing_id.name)

            # Vérifier qu'elle n'est pas rapprochée
            if operation.is_reconciled:
                raise UserError(_(
                    "Impossible d'annuler cette opération : "
                    "elle a été rapprochée avec un relevé bancaire."
                ))

            operation.write({'state': 'cancel'})
            operation.message_post(body=_("Opération annulée"))

    def action_draft(self):
        """Remet l'opération en brouillon"""
        for operation in self:
            # Vérifier qu'elle n'est pas dans une clôture validée
            if operation.closing_id and operation.closing_id.state == 'validated':
                raise UserError(_(
                    "Impossible de remettre en brouillon : "
                    "l'opération est dans le rapprochement validé '%s'."
                ) % operation.closing_id.name)

            # Vérifier qu'elle n'est pas rapprochée
            if operation.is_reconciled:
                raise UserError(_(
                    "Impossible de remettre en brouillon : "
                    "l'opération a été rapprochée."
                ))

            operation.write({'state': 'draft', 'closing_id': False})
            operation.message_post(body=_("Opération remise en brouillon"))

    def action_reconcile(self):
        """Marque l'opération comme rapprochée"""
        for operation in self:
            if operation.state != 'posted':
                raise UserError(_("Seules les opérations comptabilisées peuvent être rapprochées."))

            operation.write({
                'is_reconciled': True,
                'reconciliation_date': fields.Date.context_today(self),
                'state': 'reconciled'
            })
            operation.message_post(body=_("Opération rapprochée avec le relevé bancaire"))

    def action_unreconcile(self):
        """Annule le rapprochement de l'opération"""
        for operation in self:
            # Vérifier qu'elle n'est pas dans une clôture validée
            if operation.closing_id and operation.closing_id.state == 'validated':
                raise UserError(_(
                    "Impossible d'annuler le rapprochement : "
                    "l'opération est dans le rapprochement validé '%s'."
                ) % operation.closing_id.name)

            operation.write({
                'is_reconciled': False,
                'reconciliation_date': False,
                'state': 'posted'
            })
            operation.message_post(body=_("Rapprochement annulé"))

    def name_get(self):
        """Format d'affichage du nom"""
        result = []
        for operation in self:
            name = operation.name
            if operation.description:
                name = f"{operation.name} - {operation.description[:50]}"
            result.append((operation.id, name))
        return result
