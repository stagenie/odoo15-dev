# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partenaire',
        compute='_compute_partner_id',
        store=False,
        help='Client ou Fournisseur associé au mouvement de stock'
    )

    @api.depends('location_id', 'location_dest_id', 'picking_id.partner_id')
    def _compute_partner_id(self):
        """Calculer le partenaire depuis les emplacements ou le picking"""
        for line in self:
            partner = False

            # Essayer de récupérer le partenaire depuis le picking
            if line.picking_id and line.picking_id.partner_id:
                partner = line.picking_id.partner_id
            else:
                # Sinon, chercher dans les emplacements
                # Si l'emplacement destination est client/fournisseur
                if line.location_dest_id and line.location_dest_id.usage in ['customer', 'supplier']:
                    partner = line.location_dest_id.partner_id
                # Si l'emplacement source est client/fournisseur
                elif line.location_id and line.location_id.usage in ['customer', 'supplier']:
                    partner = line.location_id.partner_id

            line.partner_id = partner
