# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockTransferLine(models.Model):
    """
    Extension du modèle adi.stock.transfer.line pour la gestion des envois partiels.

    Ajout du champ calculé qty_not_sent pour suivre les quantités non envoyées.
    """
    _inherit = 'adi.stock.transfer.line'

    # === Champ principal: Quantité Non Envoyée ===
    qty_not_sent = fields.Float(
        string='Qté Non Envoyée',
        compute='_compute_qty_not_sent',
        digits='Product Unit of Measure',
        store=True,
        help="Quantité demandée mais non envoyée (Demandée - Envoyée)"
    )

    # === Champs informatifs ===
    is_partial_send = fields.Boolean(
        compute='_compute_is_partial_send',
        string='Envoi Partiel',
        store=True,
        help="Indique si cette ligne a fait l'objet d'un envoi partiel"
    )

    send_percentage = fields.Float(
        compute='_compute_send_percentage',
        string='% Envoyé',
        digits=(5, 1),
        help="Pourcentage de la quantité demandée qui a été envoyée"
    )

    @api.depends('quantity', 'qty_sent', 'transfer_id.state')
    def _compute_qty_not_sent(self):
        """
        Calcule la quantité non envoyée.

        qty_not_sent = quantity - qty_sent

        Note: On calcule ce champ à partir du moment où le transfert a été envoyé
        (état in_transit ou done).
        """
        for line in self:
            parent_state = line.transfer_id.state if line.transfer_id else False

            if parent_state in ('in_transit', 'done'):
                # Calcul effectif après l'envoi
                line.qty_not_sent = max(0, line.quantity - line.qty_sent)
            else:
                # Avant l'envoi, pas encore de "non envoyé"
                line.qty_not_sent = 0.0

    @api.depends('quantity', 'qty_sent', 'transfer_id.state')
    def _compute_is_partial_send(self):
        """Détermine si la ligne a fait l'objet d'un envoi partiel"""
        for line in self:
            parent_state = line.transfer_id.state if line.transfer_id else False

            if parent_state in ('in_transit', 'done'):
                line.is_partial_send = (
                    line.qty_sent > 0 and
                    line.qty_sent < line.quantity
                )
            else:
                line.is_partial_send = False

    @api.depends('quantity', 'qty_sent')
    def _compute_send_percentage(self):
        """Calcule le pourcentage envoyé"""
        for line in self:
            if line.quantity > 0:
                line.send_percentage = (line.qty_sent / line.quantity) * 100
            else:
                line.send_percentage = 0.0
