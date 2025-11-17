# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class TreasuryTransfer(models.Model):
    _inherit = 'treasury.transfer'

    # Extension du champ transfer_type pour ajouter les types bancaires
    transfer_type = fields.Selection(
        selection_add=[
            ('cash_to_bank', 'Caisse → Banque (Dépôt)'),
            ('bank_to_cash', 'Banque → Caisse (Retrait)'),
            ('safe_to_bank', 'Coffre → Banque (Dépôt)'),
            ('bank_to_safe', 'Banque → Coffre (Retrait)'),
            ('bank_to_bank', 'Banque → Banque (Virement interne)'),
        ],
        ondelete={
            'cash_to_bank': 'cascade',
            'bank_to_cash': 'cascade',
            'safe_to_bank': 'cascade',
            'bank_to_safe': 'cascade',
            'bank_to_bank': 'cascade',
        }
    )

    # Relations avec les banques
    bank_from_id = fields.Many2one(
        'treasury.bank',
        string='Banque source',
        tracking=True
    )
    bank_to_id = fields.Many2one(
        'treasury.bank',
        string='Banque destination',
        tracking=True
    )

    # Opérations bancaires créées
    bank_operation_out_id = fields.Many2one(
        'treasury.bank.operation',
        string='Opération bancaire sortie',
        readonly=True,
        ondelete='set null'
    )
    bank_operation_in_id = fields.Many2one(
        'treasury.bank.operation',
        string='Opération bancaire entrée',
        readonly=True,
        ondelete='set null'
    )

    # Soldes bancaires (pour historique)
    bank_from_balance_before = fields.Monetary(
        string='Solde banque source avant',
        currency_field='currency_id',
        readonly=True
    )
    bank_from_balance_after = fields.Monetary(
        string='Solde banque source après',
        currency_field='currency_id',
        readonly=True
    )
    bank_to_balance_before = fields.Monetary(
        string='Solde banque destination avant',
        currency_field='currency_id',
        readonly=True
    )
    bank_to_balance_after = fields.Monetary(
        string='Solde banque destination après',
        currency_field='currency_id',
        readonly=True
    )

    # Méthode de transfert
    payment_method = fields.Selection([
        ('transfer', 'Virement'),
        ('check', 'Chèque'),
        ('cash', 'Espèces'),
        ('card', 'Carte'),
        ('other', 'Autre')
    ], string='Méthode', default='transfer',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    # Référence bancaire
    bank_reference = fields.Char(
        string='Référence bancaire',
        help="Référence du virement, numéro de chèque, etc."
    )

    @api.onchange('transfer_type')
    def _onchange_transfer_type_bank(self):
        """Réinitialise les champs selon le type de transfert"""
        # Appeler la méthode parente si elle existe
        if hasattr(super(TreasuryTransfer, self), '_onchange_transfer_type'):
            super(TreasuryTransfer, self)._onchange_transfer_type()

        # Réinitialiser les champs bancaires
        if self.transfer_type not in ['cash_to_bank', 'bank_to_cash', 'safe_to_bank',
                                       'bank_to_safe', 'bank_to_bank']:
            self.bank_from_id = False
            self.bank_to_id = False
            self.payment_method = 'transfer'

        # Définir la méthode par défaut selon le type
        if self.transfer_type in ['cash_to_bank', 'bank_to_cash']:
            self.payment_method = 'cash'
        elif self.transfer_type in ['safe_to_bank', 'bank_to_safe']:
            self.payment_method = 'cash'
        elif self.transfer_type == 'bank_to_bank':
            self.payment_method = 'transfer'

    @api.constrains('transfer_type', 'cash_from_id', 'cash_to_id', 'safe_from_id',
                    'safe_to_id', 'bank_from_id', 'bank_to_id')
    def _check_transfer_consistency_bank(self):
        """Vérifie la cohérence des champs selon le type de transfert"""
        for transfer in self:
            # Vérifications pour les transferts bancaires
            if transfer.transfer_type == 'cash_to_bank':
                if not transfer.cash_from_id or not transfer.bank_to_id:
                    raise ValidationError(_(
                        "Pour un dépôt en banque, vous devez sélectionner "
                        "une caisse source et une banque destination."
                    ))
                if transfer.bank_from_id or transfer.cash_to_id or transfer.safe_from_id or transfer.safe_to_id:
                    raise ValidationError(_("Configuration de transfert incohérente."))

            elif transfer.transfer_type == 'bank_to_cash':
                if not transfer.bank_from_id or not transfer.cash_to_id:
                    raise ValidationError(_(
                        "Pour un retrait en banque, vous devez sélectionner "
                        "une banque source et une caisse destination."
                    ))
                if transfer.cash_from_id or transfer.bank_to_id or transfer.safe_from_id or transfer.safe_to_id:
                    raise ValidationError(_("Configuration de transfert incohérente."))

            elif transfer.transfer_type == 'safe_to_bank':
                if not transfer.safe_from_id or not transfer.bank_to_id:
                    raise ValidationError(_(
                        "Pour un dépôt en banque depuis le coffre, vous devez sélectionner "
                        "un coffre source et une banque destination."
                    ))
                if transfer.bank_from_id or transfer.cash_from_id or transfer.cash_to_id or transfer.safe_to_id:
                    raise ValidationError(_("Configuration de transfert incohérente."))

            elif transfer.transfer_type == 'bank_to_safe':
                if not transfer.bank_from_id or not transfer.safe_to_id:
                    raise ValidationError(_(
                        "Pour un retrait en banque vers le coffre, vous devez sélectionner "
                        "une banque source et un coffre destination."
                    ))
                if transfer.safe_from_id or transfer.cash_from_id or transfer.cash_to_id or transfer.bank_to_id:
                    raise ValidationError(_("Configuration de transfert incohérente."))

            elif transfer.transfer_type == 'bank_to_bank':
                if not transfer.bank_from_id or not transfer.bank_to_id:
                    raise ValidationError(_(
                        "Pour un virement interne, vous devez sélectionner "
                        "une banque source et une banque destination."
                    ))
                if transfer.bank_from_id == transfer.bank_to_id:
                    raise ValidationError(_(
                        "La banque source et la banque destination doivent être différentes."
                    ))
                if transfer.cash_from_id or transfer.cash_to_id or transfer.safe_from_id or transfer.safe_to_id:
                    raise ValidationError(_("Configuration de transfert incohérente."))

    def action_confirm(self):
        """Surcharge de la confirmation pour gérer les transferts bancaires"""
        for transfer in self:
            # Si c'est un transfert bancaire, créer les opérations bancaires
            if transfer.transfer_type in ['cash_to_bank', 'bank_to_cash', 'safe_to_bank',
                                          'bank_to_safe', 'bank_to_bank']:
                transfer._create_bank_operations()

        # Appeler la méthode parente pour les autres types
        return super(TreasuryTransfer, self).action_confirm()

    def _create_bank_operations(self):
        """Crée les opérations bancaires pour le transfert"""
        self.ensure_one()

        # Catégories pour les transferts
        cat_transfer_in = self.env['treasury.operation.category'].search([
            ('code', '=', 'BANK_TRANSFER_IN')
        ], limit=1)
        cat_transfer_out = self.env['treasury.operation.category'].search([
            ('code', '=', 'BANK_TRANSFER_OUT')
        ], limit=1)

        if not cat_transfer_in or not cat_transfer_out:
            # Fallback sur les catégories génériques
            cat_transfer_in = self.env['treasury.operation.category'].search([
                ('code', '=', 'TRANSFER_IN')
            ], limit=1)
            cat_transfer_out = self.env['treasury.operation.category'].search([
                ('code', '=', 'TRANSFER_OUT')
            ], limit=1)

        # Créer les opérations selon le type de transfert
        if self.transfer_type == 'cash_to_bank':
            # Sortie de caisse (déjà géré par le module parent)
            # Entrée en banque
            self._create_bank_operation_in(cat_transfer_in)

        elif self.transfer_type == 'bank_to_cash':
            # Sortie de banque
            self._create_bank_operation_out(cat_transfer_out)
            # Entrée en caisse (déjà géré par le module parent)

        elif self.transfer_type == 'safe_to_bank':
            # Sortie de coffre (déjà géré par le module parent)
            # Entrée en banque
            self._create_bank_operation_in(cat_transfer_in)

        elif self.transfer_type == 'bank_to_safe':
            # Sortie de banque
            self._create_bank_operation_out(cat_transfer_out)
            # Entrée en coffre (déjà géré par le module parent)

        elif self.transfer_type == 'bank_to_bank':
            # Sortie de banque source
            self._create_bank_operation_out(cat_transfer_out)
            # Entrée en banque destination
            self._create_bank_operation_in(cat_transfer_in)

    def _create_bank_operation_out(self, category):
        """Crée l'opération de sortie bancaire"""
        self.ensure_one()

        # Sauvegarder le solde avant
        self.bank_from_balance_before = self.bank_from_id.current_balance

        # Créer l'opération de sortie
        operation_out = self.env['treasury.bank.operation'].create({
            'name': self.env['ir.sequence'].next_by_code('treasury.bank.operation'),
            'bank_id': self.bank_from_id.id,
            'operation_type': 'out',
            'category_id': category.id if category else False,
            'amount': self.amount,
            'date': fields.Datetime.now(),
            'value_date': fields.Date.context_today(self),
            'description': _('Transfert vers %s - %s') % (
                self._get_destination_name(), self.name
            ),
            'payment_method': self.payment_method,
            'bank_reference': self.bank_reference,
            'transfer_id': self.id,
            'is_manual': False,
            'state': 'posted',
        })

        self.bank_operation_out_id = operation_out

        # Sauvegarder le solde après
        self.bank_from_balance_after = self.bank_from_id.current_balance

    def _create_bank_operation_in(self, category):
        """Crée l'opération d'entrée bancaire"""
        self.ensure_one()

        # Sauvegarder le solde avant
        self.bank_to_balance_before = self.bank_to_id.current_balance

        # Créer l'opération d'entrée
        operation_in = self.env['treasury.bank.operation'].create({
            'name': self.env['ir.sequence'].next_by_code('treasury.bank.operation'),
            'bank_id': self.bank_to_id.id,
            'operation_type': 'in',
            'category_id': category.id if category else False,
            'amount': self.amount,
            'date': fields.Datetime.now(),
            'value_date': fields.Date.context_today(self),
            'description': _('Transfert depuis %s - %s') % (
                self._get_source_name(), self.name
            ),
            'payment_method': self.payment_method,
            'bank_reference': self.bank_reference,
            'transfer_id': self.id,
            'is_manual': False,
            'state': 'posted',
        })

        self.bank_operation_in_id = operation_in

        # Sauvegarder le solde après
        self.bank_to_balance_after = self.bank_to_id.current_balance

    def _get_source_name(self):
        """Retourne le nom de la source du transfert"""
        self.ensure_one()
        if self.cash_from_id:
            return self.cash_from_id.name
        elif self.safe_from_id:
            return self.safe_from_id.name
        elif self.bank_from_id:
            return self.bank_from_id.name
        return _('Source inconnue')

    def _get_destination_name(self):
        """Retourne le nom de la destination du transfert"""
        self.ensure_one()
        if self.cash_to_id:
            return self.cash_to_id.name
        elif self.safe_to_id:
            return self.safe_to_id.name
        elif self.bank_to_id:
            return self.bank_to_id.name
        return _('Destination inconnue')

    def action_cancel(self):
        """Surcharge de l'annulation pour supprimer les opérations bancaires"""
        for transfer in self:
            # Supprimer les opérations bancaires si elles existent
            if transfer.bank_operation_out_id:
                transfer.bank_operation_out_id.unlink()
            if transfer.bank_operation_in_id:
                transfer.bank_operation_in_id.unlink()

        # Appeler la méthode parente
        return super(TreasuryTransfer, self).action_cancel()

    def name_get(self):
        """Format d'affichage du nom avec infos bancaires"""
        result = []
        for transfer in self:
            name = transfer.name
            if transfer.transfer_type in ['cash_to_bank', 'bank_to_cash', 'safe_to_bank',
                                          'bank_to_safe', 'bank_to_bank']:
                type_label = dict(transfer._fields['transfer_type'].selection).get(transfer.transfer_type, '')
                name = f"{transfer.name} - {type_label}"
            result.append((transfer.id, name))
        return result if result else super(TreasuryTransfer, self).name_get()
