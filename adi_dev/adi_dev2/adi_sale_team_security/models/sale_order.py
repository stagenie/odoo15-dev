from odoo import api, fields, models, _
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('team_id')
    def _onchange_team_id(self):
        print(self.env.user.team_id)
        if not self.env.user.has_group('sales_team.group_sale_manager'):            
            if self.create_uid and self.create_uid != self.env.user:
                _logger.warning("Tentative de modification non autorisée de l'équipe")
                raise AccessError(_("Seuls les responsables des ventes peuvent modifier l'équipe commerciale."))

    def write(self, vals):
        if 'team_id' in vals and not self.env.user.has_group('sales_team.group_sale_manager'):
            for record in self:
                if record.create_uid and record.create_uid != self.env.user:
                    _logger.warning("Tentative de modification non autorisée de l'équipe via write")
                    raise AccessError(_("Seuls les responsables des ventes peuvent modifier l'équipe commerciale."))
        return super(SaleOrder, self).write(vals)

    """ 
    @api.model_create_multi
    def create(self, vals_list):
        # Permettre la création initiale avec une équipe
        return super(SaleOrder, self).create(vals_list)
    """