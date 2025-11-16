from odoo import api, fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    sale_team_access = fields.Selection([
        ('own', 'Own Documents Only'),
        ('team', 'Sales Team Documents'),
        ('all', 'All Documents'),
    ], string='Sales Access Level', default='own')
    
    sale_team_ids = fields.Many2many(
        'crm.team',
        'sale_team_users_rel',
        'user_id',
        'team_id',
        string='Sales Teams'
    )

    @api.onchange('sale_team_access')
    def _onchange_sale_team_access(self):
        if self.sale_team_access == 'own':
            self.sale_team_ids = False