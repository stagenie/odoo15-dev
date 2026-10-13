# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.tools import float_compare, format_amount


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_net_price_unit(self):
        """Prix unitaire HT après remise."""
        self.ensure_one()
        return self.price_unit * (1.0 - (self.discount or 0.0) / 100.0)

    def _is_below_cost(self):
        self.ensure_one()
        if self.display_type or not self.product_id or self.purchase_price <= 0:
            return False
        precision = self.env['decimal.precision'].precision_get('Product Price')
        return float_compare(self._get_net_price_unit(), self.purchase_price,
                             precision_digits=precision) < 0

    # Odoo exécute les onchanges d'un champ par ordre alphabétique du nom de
    # méthode (getmembers) : le nom commence par « w » pour passer après
    # product_id_change / product_uom_change, qui fixent le prix unitaire.
    @api.onchange('product_id', 'product_uom', 'product_uom_qty', 'price_unit', 'discount')
    def warning_price_below_cost_onchange(self):
        """Avertir (sans bloquer) si le prix net est inférieur au coût."""
        if len(self) != 1 or not self._is_below_cost():
            return

        currency = self.currency_id or self.order_id.currency_id or self.env.company.currency_id
        product = self.product_id.display_name
        if self.env.user.has_group('adi_hide_cost_margin.group_show_cost'):
            net_price = self._get_net_price_unit()
            message = _(
                "Article : %(product)s\n\n"
                "Prix unitaire : %(price)s\n"
                "Remise : %(discount)s %%\n"
                "Prix net : %(net)s\n"
                "Coût unitaire : %(cost)s\n"
                "Perte unitaire : %(loss)s\n\n"
                "Le prix de vente net est inférieur au coût du produit."
            ) % {
                'product': product,
                'price': format_amount(self.env, self.price_unit, currency),
                'discount': self.discount or 0.0,
                'net': format_amount(self.env, net_price, currency),
                'cost': format_amount(self.env, self.purchase_price, currency),
                'loss': format_amount(self.env, self.purchase_price - net_price, currency),
            }
        else:
            message = _(
                "Article : %(product)s\n\n"
                "Le prix de vente net (après remise) est inférieur au coût du produit."
            ) % {'product': product}

        return {
            'warning': {
                'title': _("Prix de vente inférieur au coût"),
                'message': message,
            }
        }
