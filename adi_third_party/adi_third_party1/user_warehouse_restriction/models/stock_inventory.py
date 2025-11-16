# models/stock_inventory.py

from odoo import models, fields, api

class Inventory(models.Model):
    _inherit = "stock.inventory"

    def _get_inventory_lines_values(self):
        # Récupérer les emplacements des entrepôts autorisés pour l'utilisateur
        allowed_locations = self.env['stock.location']
        for warehouse in self.env.user.warehouse_ids:
            allowed_locations |= warehouse.view_location_id

        # Filtrer les lignes d'inventaire en fonction des emplacements autorisés
        domain = [('location_id', 'in', allowed_locations.ids)]
        vals = super(Inventory, self)._get_inventory_lines_values(domain)
        return vals

    @api.onchange('location_ids')
    def _onchange_location_ids(self):
        # Restreindre la sélection des emplacements aux entrepôts autorisés
        allowed_locations = self.env['stock.location']
        for warehouse in self.env.user.warehouse_ids:
            allowed_locations |= warehouse.view_location_id
        return {'domain': {'location_ids': [('id', 'in', allowed_locations.ids)]}}