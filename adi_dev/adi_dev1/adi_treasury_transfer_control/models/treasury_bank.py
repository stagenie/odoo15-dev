# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TreasuryBankControl(models.Model):
    _inherit = 'treasury.bank'

    # =========================================================================
    # CHAMPS DE CONTRÔLE
    # =========================================================================

    allow_negative_balance = fields.Boolean(
        string='Autoriser solde négatif',
        default=True,
        help="Si coché, ce compte peut avoir un solde négatif "
             "(dans la limite du découvert autorisé)."
    )

    control_level = fields.Selection([
        ('none', 'Aucun contrôle'),
        ('warning', 'Avertissement'),
        ('blocking', 'Bloquant'),
    ], string='Niveau de contrôle',
        default='blocking',
        help="Niveau de contrôle pour les transferts sortants:\n"
             "- Aucun: Pas de vérification de solde\n"
             "- Avertissement: Message d'alerte mais transfert autorisé\n"
             "- Bloquant: Transfert refusé si découvert dépassé"
    )

    min_balance = fields.Monetary(
        string='Solde minimum conseillé',
        currency_field='currency_id',
        default=0,
        help="Solde minimum recommandé. Un avertissement sera affiché "
             "si le solde descend en dessous."
    )

    transfer_out_count = fields.Integer(
        string='Transferts sortants',
        compute='_compute_transfer_counts',
        help="Nombre de transferts sortants en attente"
    )

    transfer_in_count = fields.Integer(
        string='Transferts entrants',
        compute='_compute_transfer_counts',
        help="Nombre de transferts entrants en attente"
    )

    pending_transfer_amount = fields.Monetary(
        string='Montant en transit',
        currency_field='currency_id',
        compute='_compute_pending_transfer_amount',
        help="Montant total des transferts en attente"
    )

    effective_available_balance = fields.Monetary(
        string='Solde réellement disponible',
        currency_field='currency_id',
        compute='_compute_effective_available_balance',
        help="Solde disponible moins les transferts sortants en attente"
    )

    overdraft_remaining = fields.Monetary(
        string='Découvert restant',
        currency_field='currency_id',
        compute='_compute_overdraft_remaining',
        help="Montant de découvert encore utilisable"
    )

    # =========================================================================
    # CALCULS
    # =========================================================================

    def _compute_transfer_counts(self):
        """Calculer le nombre de transferts en attente"""
        Transfer = self.env['treasury.transfer']
        for bank in self:
            bank.transfer_out_count = Transfer.search_count([
                ('bank_from_id', '=', bank.id),
                ('state', 'in', ['draft', 'confirm']),
            ])
            bank.transfer_in_count = Transfer.search_count([
                ('bank_to_id', '=', bank.id),
                ('state', 'in', ['draft', 'confirm']),
            ])

    def _compute_pending_transfer_amount(self):
        """Calculer le montant des transferts en transit"""
        Transfer = self.env['treasury.transfer']
        for bank in self:
            # Transferts sortants confirmés
            out_transfers = Transfer.search([
                ('bank_from_id', '=', bank.id),
                ('state', '=', 'confirm'),
            ])
            out_amount = sum(out_transfers.mapped('amount'))

            # Transferts entrants confirmés
            in_transfers = Transfer.search([
                ('bank_to_id', '=', bank.id),
                ('state', '=', 'confirm'),
            ])
            in_amount = sum(in_transfers.mapped('amount'))

            bank.pending_transfer_amount = out_amount - in_amount

    def _compute_effective_available_balance(self):
        """Calculer le solde effectivement disponible"""
        for bank in self:
            Transfer = self.env['treasury.transfer']
            pending_out = Transfer.search([
                ('bank_from_id', '=', bank.id),
                ('state', 'in', ['draft', 'confirm']),
            ])
            pending_amount = sum(pending_out.mapped('amount'))

            # Utiliser le solde disponible (basé sur date de valeur)
            base_balance = getattr(bank, 'available_balance', bank.current_balance)
            bank.effective_available_balance = base_balance - pending_amount

    def _compute_overdraft_remaining(self):
        """Calculer le découvert restant disponible"""
        for bank in self:
            if bank.current_balance >= 0:
                # Si solde positif, tout le découvert est disponible
                bank.overdraft_remaining = bank.overdraft_limit
            else:
                # Si solde négatif, calculer ce qui reste
                bank.overdraft_remaining = max(
                    0,
                    bank.overdraft_limit + bank.current_balance
                )

    # =========================================================================
    # CONTRAINTES
    # =========================================================================

    @api.constrains('min_balance', 'overdraft_limit')
    def _check_balance_limits(self):
        """Vérifier la cohérence des limites"""
        for bank in self:
            if bank.min_balance < -bank.overdraft_limit:
                raise ValidationError(
                    _("Le solde minimum (%s) ne peut pas être inférieur au "
                      "découvert autorisé (-%s) pour le compte '%s'.") % (
                        bank.min_balance,
                        bank.overdraft_limit,
                        bank.name
                    )
                )

    # =========================================================================
    # MÉTHODES D'ACTION
    # =========================================================================

    def action_view_pending_transfers(self):
        """Voir les transferts en attente"""
        self.ensure_one()
        return {
            'name': _('Transferts en attente - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.transfer',
            'view_mode': 'tree,form',
            'domain': [
                '|',
                ('bank_from_id', '=', self.id),
                ('bank_to_id', '=', self.id),
                ('state', 'in', ['draft', 'confirm']),
            ],
            'context': {
                'default_bank_from_id': self.id,
            },
        }

    def get_balance_status(self):
        """Retourner le statut du solde"""
        self.ensure_one()

        if self.current_balance < -self.overdraft_limit:
            return {
                'status': 'overdraft_exceeded',
                'color': 'danger',
                'message': _('Découvert dépassé'),
            }
        elif self.current_balance < 0:
            return {
                'status': 'overdraft',
                'color': 'warning',
                'message': _('En découvert'),
            }
        elif self.min_balance and self.current_balance < self.min_balance:
            return {
                'status': 'low',
                'color': 'info',
                'message': _('Solde bas'),
            }
        else:
            return {
                'status': 'normal',
                'color': 'success',
                'message': _('Solde normal'),
            }

    def get_transfer_capacity(self):
        """Calculer la capacité de transfert maximale"""
        self.ensure_one()

        if self.allow_negative_balance:
            # Solde actuel + découvert autorisé
            return self.current_balance + self.overdraft_limit
        else:
            # Seulement le solde positif
            return max(0, self.current_balance)
