# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class TreasuryCashClosing(models.Model):
    _inherit = 'treasury.cash.closing'

    # Lignes de comptage
    count_line_ids = fields.One2many(
        'treasury.cash.closing.count',
        'closing_id',
        string='Comptage des billets et pièces',
        help="Détail du comptage par dénomination"
    )

    # Total du comptage
    counted_total = fields.Monetary(
        string='Total compté',
        currency_field='currency_id',
        compute='_compute_counted_total',
        store=True,
        help="Montant total calculé à partir du comptage des billets et pièces"
    )

    # Indicateur si le comptage est utilisé
    use_cash_count = fields.Boolean(
        string='Utiliser le comptage',
        default=True,
        help="Si coché, le solde réel sera calculé automatiquement à partir du comptage"
    )

    @api.depends('count_line_ids.subtotal')
    def _compute_counted_total(self):
        """Calculer le total à partir des lignes de comptage"""
        for closing in self:
            closing.counted_total = sum(closing.count_line_ids.mapped('subtotal'))

    @api.onchange('counted_total', 'use_cash_count')
    def _onchange_counted_total(self):
        """Mettre à jour le solde réel quand le total compté change"""
        for closing in self:
            if closing.use_cash_count and closing.counted_total and closing.counted_total > 0:
                closing.balance_end_real = closing.counted_total
                # Marquer comme modifié manuellement pour éviter la synchro auto
                closing.balance_end_real_manual = True

    def action_auto_fill_count_lines(self):
        """Pré-remplir les lignes de comptage avec toutes les dénominations actives"""
        self.ensure_one()

        # Supprimer les lignes existantes
        self.count_line_ids.unlink()

        # Récupérer toutes les dénominations actives pour cette devise
        denominations = self.env['cash.denomination'].search([
            ('currency_id', '=', self.currency_id.id),
            ('active', '=', True)
        ], order='value desc')

        # Créer une ligne pour chaque dénomination
        count_lines = []
        for denomination in denominations:
            count_lines.append((0, 0, {
                'denomination_id': denomination.id,
                'quantity': 0,
            }))

        self.count_line_ids = count_lines

        # Recharger le formulaire pour afficher les lignes créées
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.cash.closing',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_clear_count_lines(self):
        """Réinitialiser toutes les quantités à 0"""
        self.ensure_one()
        for line in self.count_line_ids:
            line.quantity = 0

        # Recharger le formulaire pour afficher les changements
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.cash.closing',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }
