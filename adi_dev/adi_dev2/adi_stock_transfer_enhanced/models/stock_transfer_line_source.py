# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockTransferLineSource(models.Model):
    """
    Modèle pour tracer les emplacements sources utilisés pour chaque ligne de transfert.

    Quand un transfert utilise la réservation multi-source, ce modèle enregistre
    la répartition des quantités par emplacement source.

    Exemple:
        Ligne: Produit A - 50 unités demandées
        Sources:
            - A1/WH/Stock: 20 unités
            - A2/WH/Stock: 15 unités
            - A3/WH/Stock: 15 unités
    """
    _name = 'adi.stock.transfer.line.source'
    _description = 'Détail des sources par ligne de transfert'
    _order = 'location_id'

    # === Relations ===
    line_id = fields.Many2one(
        'adi.stock.transfer.line',
        string='Ligne de Transfert',
        required=True,
        ondelete='cascade',
        index=True
    )
    transfer_id = fields.Many2one(
        related='line_id.transfer_id',
        store=True,
        string='Transfert'
    )
    product_id = fields.Many2one(
        related='line_id.product_id',
        store=True,
        string='Produit'
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Emplacement Source',
        required=True,
        index=True
    )

    # === Quantités ===
    quantity_reserved = fields.Float(
        string='Qté Réservée',
        digits='Product Unit of Measure',
        help="Quantité réservée dans cet emplacement"
    )
    quantity_done = fields.Float(
        string='Qté Traitée',
        digits='Product Unit of Measure',
        help="Quantité effectivement prélevée de cet emplacement"
    )

    # === Traçabilité Odoo ===
    move_line_id = fields.Many2one(
        'stock.move.line',
        string='Ligne de Mouvement',
        help="Référence vers la ligne de mouvement Odoo correspondante"
    )

    # === Affichage ===
    location_name = fields.Char(
        related='location_id.complete_name',
        string='Emplacement'
    )

    def name_get(self):
        """Affichage: [Emplacement] Qté unités"""
        result = []
        for record in self:
            name = f"[{record.location_id.name}] {record.quantity_reserved} {record.line_id.product_uom_id.name or ''}"
            result.append((record.id, name))
        return result
