# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TreasurySafeControl(models.Model):
    _inherit = 'treasury.safe'

    # =========================================================================
    # CHAMPS DE CONTRÔLE
    # =========================================================================

    allow_negative_balance = fields.Boolean(
        string='Autoriser solde négatif',
        default=False,
        help="Si coché, ce coffre peut avoir un solde négatif. "
             "Généralement non recommandé pour les coffres physiques."
    )

    min_balance = fields.Monetary(
        string='Solde minimum',
        currency_field='currency_id',
        default=0,
        help="Solde minimum à maintenir dans ce coffre."
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
        help="Montant total des transferts en attente"
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
        for safe in self:
            safe.transfer_out_count = Transfer.search_count([
                ('safe_from_id', '=', safe.id),
                ('state', 'in', ['draft', 'confirm']),
            ])
            safe.transfer_in_count = Transfer.search_count([
                ('safe_to_id', '=', safe.id),
                ('state', 'in', ['draft', 'confirm']),
            ])

    def _compute_pending_transfer_amount(self):
        """Calculer le montant des transferts en transit"""
        Transfer = self.env['treasury.transfer']
        for safe in self:
            # Transferts sortants confirmés
            out_transfers = Transfer.search([
                ('safe_from_id', '=', safe.id),
                ('state', '=', 'confirm'),
            ])
            out_amount = sum(out_transfers.mapped('amount'))

            # Transferts entrants confirmés
            in_transfers = Transfer.search([
                ('safe_to_id', '=', safe.id),
                ('state', '=', 'confirm'),
            ])
            in_amount = sum(in_transfers.mapped('amount'))

            safe.pending_transfer_amount = out_amount - in_amount

    def _compute_available_balance(self):
        """Calculer le solde disponible"""
        for safe in self:
            Transfer = self.env['treasury.transfer']
            pending_out = Transfer.search([
                ('safe_from_id', '=', safe.id),
                ('state', 'in', ['draft', 'confirm']),
            ])
            pending_amount = sum(pending_out.mapped('amount'))
            safe.available_balance = safe.current_balance - pending_amount

    # =========================================================================
    # CONTRAINTES
    # =========================================================================

    @api.constrains('min_balance')
    def _check_min_balance(self):
        """Vérifier que le solde minimum est valide"""
        for safe in self:
            if safe.min_balance < 0 and not safe.allow_negative_balance:
                raise ValidationError(
                    _("Le solde minimum ne peut pas être négatif si le solde "
                      "négatif n'est pas autorisé pour le coffre '%s'.") % safe.name
                )

    @api.constrains('min_balance', 'max_capacity')
    def _check_balance_limits(self):
        """Vérifier la cohérence des limites"""
        for safe in self:
            max_cap = getattr(safe, 'max_capacity', 0)
            if max_cap > 0 and safe.min_balance > max_cap:
                raise ValidationError(
                    _("Le solde minimum (%s) ne peut pas être supérieur à "
                      "la capacité maximale (%s) pour le coffre '%s'.") % (
                        safe.min_balance,
                        max_cap,
                        safe.name
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
                ('safe_from_id', '=', self.id),
                ('safe_to_id', '=', self.id),
                ('state', 'in', ['draft', 'confirm']),
            ],
            'context': {
                'default_safe_from_id': self.id,
            },
        }

    def get_balance_status(self):
        """Retourner le statut du solde"""
        self.ensure_one()

        max_cap = getattr(self, 'max_capacity', 0)

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
        elif max_cap and self.current_balance >= max_cap * 0.9:
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
