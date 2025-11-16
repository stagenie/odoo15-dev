from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    allowed_warehouse_ids = fields.Many2many(
        comodel_name='stock.warehouse',
        string='Allowed Warehouses',
        help='Allowed Warehouses for the user.'
    )
    allowed_location_ids = fields.Many2many(
        comodel_name='stock.location',        
        string='Allowed Locations',
        compute='_compute_allowed_locations',        
        help='Allowed Stock Locations for the user based on allowed warehouses.'
    )

    @api.depends('allowed_warehouse_ids')
    def _compute_allowed_locations(self):
        """
        Cette fonction calcule les emplacements physiques autorisés pour un utilisateur
        en fonction des entrepôts autorisés.
        """
        for user in self:
            # Initialiser un ensemble vide pour stocker les emplacements autorisés
            allowed_locations = self.env['stock.location']
            
            # Parcourir les entrepôts autorisés
            for warehouse in user.allowed_warehouse_ids:
                # Ajouter les emplacements physiques (child_ids) de l'entrepôt
                allowed_locations |= self.env['stock.location'].search([
                    ('id', 'child_of', warehouse.view_location_id.id),  # Inclure les emplacements enfants
                    ('usage', '=', 'internal')  # Filtrer uniquement les emplacements physiques
                ])
            
            # Assigner les emplacements trouvés au champ allowed_location_ids
            user.allowed_location_ids = allowed_locations