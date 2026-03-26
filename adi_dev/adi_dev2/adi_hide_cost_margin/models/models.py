from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    margin = fields.Float(groups="adi_hide_cost_margin.group_show_margin")


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    purchase_price = fields.Float(groups="adi_hide_cost_margin.group_show_cost")
    margin = fields.Float(groups="adi_hide_cost_margin.group_show_margin")
    margin_percent = fields.Float(groups="adi_hide_cost_margin.group_show_margin")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    standard_price = fields.Float(groups="adi_hide_cost_margin.group_show_cost")


class ProductProduct(models.Model):
    _inherit = "product.product"

    standard_price = fields.Float(groups="adi_hide_cost_margin.group_show_cost")


class SaleReport(models.Model):
    _inherit = "sale.report"

    margin = fields.Float(groups="adi_hide_cost_margin.group_show_margin")


class ResUsers(models.Model):
    _inherit = "res.users"

    show_cost = fields.Boolean(string="Voir le Coût", compute="_compute_show_cost")
    show_margin = fields.Boolean(string="Voir la Marge", compute="_compute_show_margin")

    def _compute_show_cost(self):
        for user in self:
            user.show_cost = user.has_group('adi_hide_cost_margin.group_show_cost')

    def _compute_show_margin(self):
        for user in self:
            user.show_margin = user.has_group('adi_hide_cost_margin.group_show_margin')

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        group_cost = self.env.ref('adi_hide_cost_margin.group_show_cost', raise_if_not_found=False)
        if group_cost:
            for user in users:
                if user.has_group('base.group_user'):
                    user.write({'groups_id': [(4, group_cost.id)]})
        return users
