from odoo import api, fields, models


class StockTransfer(models.Model):
    _inherit = 'adi.stock.transfer'

    dest_responsible_id = fields.Many2one(
        'res.users',
        string="Responsable reception",
        help="Personne responsable de la reception du transfert a destination."
    )

    source_team_id = fields.Many2one(
        'crm.team',
        string="Equipe source",
        compute='_compute_teams',
        store=True,
        help="Equipe commerciale de l'entrepot source."
    )

    dest_team_id = fields.Many2one(
        'crm.team',
        string="Equipe destination",
        compute='_compute_teams',
        store=True,
        help="Equipe commerciale de l'entrepot destination."
    )

    @api.depends('source_warehouse_id', 'dest_warehouse_id',
                 'source_warehouse_id.team_id', 'dest_warehouse_id.team_id')
    def _compute_teams(self):
        for transfer in self:
            transfer.source_team_id = transfer.source_warehouse_id.team_id
            transfer.dest_team_id = transfer.dest_warehouse_id.team_id
