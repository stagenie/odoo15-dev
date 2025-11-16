from odoo import models, fields, api


from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"

    margin = fields.Float(groups="adi_hide_cost_margin.group_show_margin")


class ResUsers(models.Model):
    _inherit = "res.users"

    show_margin = fields.Boolean(string="Afficher la Marge", compute="_compute_show_margin")

    def _compute_show_margin(self):
        for user in self:
            user.show_margin = self.env.user.has_group('adi_hide_cost_margin.group_show_margin')
