from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    team_id = fields.Many2one(
        'crm.team',
        string="Equipe commerciale",
        help="Equipe commerciale associee a cet entrepot. "
             "Utilisee pour les en-tetes des rapports de transfert."
    )
