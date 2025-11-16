from odoo import models, fields, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def product_catelog(self):
        cart_object = self.env["sale.order.line"]
        product_object = self.env["product.product"]
        cart_products_details = cart_object.search(
            [('order_id', "=", self.id)]) # , ("cart_flag", "=", True)
        product_object_data = product_object.search(
                [("_quantity", "!=", 0)])
        for rec in product_object_data:
            rec._quantity = 0
        if len(cart_products_details) > 0:
            for rec in cart_products_details:
                assign_quantity = rec.product_uom_qty
                rec.product_id._quantity = assign_quantity
        # else:
        #     product_object_data = product_object.search(
        #         [("_quantity", "!=", 0)])
        #     for rec in product_object_data:
        #         rec._quantity = 0

        kanban_view = self.env.ref(
            'sttl_product_catalog_so.product_product_view_kanban')

        return {
            'type': 'ir.actions.act_window',
            'name': _('Choose Products'),
            'res_model': 'product.product',
            'views': [(kanban_view.id, 'kanban')],
            'context': {
                # '_quantity_change': True,
                'sale_id': self.id,
                'create': False
            },
            'help': _("""<p class="o_view_nocontent_smiling_face">
                            Create a new product
                        </p>""")
        }

    def sol_by_cart(self, operation, product_id, sale_id):
        """
        Create Sale Order Line By
        Cart Functionality
        """

        sol_object = self.env["sale.order.line"]

        sol_data = dict()
        sol_data["product_id"] = product_id.id
        sol_data["order_id"] = sale_id.id
        sol_data["price_unit"] = product_id.lst_price
        sol_data["product_uom"] = product_id.uom_id.id

        if operation == "add":
            sol_data["product_uom_qty"] = product_id._quantity
            # sol_data["cart_flag"] = True
            sol_object.create(sol_data)
            return

        sol_ = sol_object.search(
            [('order_id', '=', sale_id.id), ('product_id', '=', product_id.id), ]) # ("cart_flag", "=", True)

        if operation == "remove":
            if product_id._quantity <= 0:
                product_id._quantity = 0
                sol_.unlink()
                return
            sol_["product_uom_qty"] = product_id._quantity

        elif operation == "update":
            sol_["product_uom_qty"] = product_id._quantity
        return

    def user_input_qty_sol(self, _qty, product_id, sale_id):
        sol_object = self.env["sale.order.line"]
        product_object = self.env["product.product"]
        cart_product_details = sol_object.search(
            [('order_id', "=", sale_id), ("product_id", "=", product_id)
             ]) # ("cart_flag", "=", True)

        if len(cart_product_details) > 0:
            cart_product_details.product_uom_qty = _qty
            cart_product_details.product_id._quantity = _qty
            if _qty == 0:
                cart_product_details.unlink()
            return
        else:
            if _qty == 0:
                return
            product_id = product_object.search([('id', '=', product_id)])
            sol_data = dict()
            sol_data["product_id"] = product_id.id
            sol_data["order_id"] = sale_id
            sol_data["price_unit"] = product_id.lst_price
            sol_data["product_uom"] = product_id.uom_id.id
            sol_data["product_uom_qty"] = _qty
            # sol_data["cart_flag"] = True
            so = sol_object.create(sol_data)
            so.product_id._quantity = _qty
            return


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    cart_flag = fields.Boolean("Cart Flag", default=False)

    def unlink(self):
        self.product_id._quantity = 0
        return super().unlink()
