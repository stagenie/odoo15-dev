# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_date = fields.Date(
        string="Date de livraison prévue",
        help="Date prévue pour la livraison de la commande."
    )

    def action_confirm(self):
        """
        Hérite la méthode de confirmation pour transférer la date de livraison
        dans les bons de livraison.
        """
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            pickings = order.picking_ids.filtered(lambda p: p.state not in ('done', 'cancel'))
            for picking in pickings:
                picking.scheduled_date = order.delivery_date
        return res

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    scheduled_date = fields.Datetime(
        string="Date de livraison prévue",
        help="Date prévue pour cette livraison."
    )
