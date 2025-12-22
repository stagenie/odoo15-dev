# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TreasuryCashControl(models.Model):
    _inherit = 'treasury.cash'

    # =========================================================================
    # CHAMPS DE CONTRÔLE
    # =========================================================================

    allow_negative_balance = fields.Boolean(
        string='Autoriser solde négatif',
        default=False,
        help="Si coché, cette caisse peut avoir un solde négatif. "
             "Ceci est utile pour les caisses de dépannage ou temporaires."
    )

    min_balance = fields.Monetary(
        string='Solde minimum',
        currency_field='currency_id',
        default=0,
        help="Solde minimum à maintenir dans cette caisse. "
             "Un avertissement sera affiché si le solde descend en dessous."
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
             "- Bloquant: Transfert refusé si solde insuffisant"
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
        help="Montant total des transferts en attente (confirmés mais non effectués)"
    )

    available_balance = fields.Monetary(
        string='Solde disponible',
        currency_field='currency_id',
        compute='_compute_available_balance',
        help="Solde actuel moins les transferts sortants en attente"
    )

    # =========================================================================
    # CALCULS
    # =========================================================================

    def _compute_transfer_counts(self):
        """Calculer le nombre de transferts en attente"""
        Transfer = self.env['treasury.transfer']
        for cash in self:
            cash.transfer_out_count = Transfer.search_count([
                ('cash_from_id', '=', cash.id),
                ('state', 'in', ['draft', 'confirm']),
            ])
            cash.transfer_in_count = Transfer.search_count([
                ('cash_to_id', '=', cash.id),
                ('state', 'in', ['draft', 'confirm']),
            ])

    def _compute_pending_transfer_amount(self):
        """Calculer le montant des transferts en transit"""
        Transfer = self.env['treasury.transfer']
        for cash in self:
            # Transferts sortants confirmés (en attente de validation finale)
            out_transfers = Transfer.search([
                ('cash_from_id', '=', cash.id),
                ('state', '=', 'confirm'),
            ])
            out_amount = sum(out_transfers.mapped('amount'))

            # Transferts entrants confirmés (en attente de validation finale)
            in_transfers = Transfer.search([
                ('cash_to_id', '=', cash.id),
                ('state', '=', 'confirm'),
            ])
            in_amount = sum(in_transfers.mapped('amount'))

            # Montant net en transit (sortants - entrants)
            cash.pending_transfer_amount = out_amount - in_amount

    def _compute_available_balance(self):
        """Calculer le solde disponible (après transferts en attente)"""
        for cash in self:
            # Récupérer les transferts sortants en brouillon également
            Transfer = self.env['treasury.transfer']
            pending_out = Transfer.search([
                ('cash_from_id', '=', cash.id),
                ('state', 'in', ['draft', 'confirm']),
            ])
            pending_amount = sum(pending_out.mapped('amount'))

            cash.available_balance = cash.current_balance - pending_amount

    # =========================================================================
    # CONTRAINTES
    # =========================================================================

    @api.constrains('min_balance')
    def _check_min_balance(self):
        """Vérifier que le solde minimum est valide"""
        for cash in self:
            if cash.min_balance < 0 and not cash.allow_negative_balance:
                raise ValidationError(
                    _("Le solde minimum ne peut pas être négatif si le solde "
                      "négatif n'est pas autorisé pour la caisse '%s'.") % cash.name
                )

    @api.constrains('min_balance', 'max_amount')
    def _check_balance_limits(self):
        """Vérifier la cohérence des limites"""
        for cash in self:
            if cash.max_amount > 0 and cash.min_balance > cash.max_amount:
                raise ValidationError(
                    _("Le solde minimum (%s) ne peut pas être supérieur au "
                      "montant maximum (%s) pour la caisse '%s'.") % (
                        cash.min_balance,
                        cash.max_amount,
                        cash.name
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
                ('cash_from_id', '=', self.id),
                ('cash_to_id', '=', self.id),
                ('state', 'in', ['draft', 'confirm']),
            ],
            'context': {
                'default_cash_from_id': self.id,
            },
        }

    def get_balance_status(self):
        """Retourner le statut du solde pour affichage"""
        self.ensure_one()

        if self.current_balance < 0:
            return {
                'status': 'negative',
                'color': 'danger',
                'message': _('Solde négatif'),
            }
        elif self.min_balance and self.current_balance < self.min_balance:
            return {
                'status': 'low',
                'color': 'warning',
                'message': _('Solde bas'),
            }
        elif self.max_amount and self.current_balance >= self.max_amount * 0.9:
            return {
                'status': 'high',
                'color': 'info',
                'message': _('Proche du maximum'),
            }
        else:
            return {
                'status': 'normal',
                'color': 'success',
                'message': _('Solde normal'),
            }
