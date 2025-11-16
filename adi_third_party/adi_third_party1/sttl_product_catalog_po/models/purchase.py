from odoo import  models, fields, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def product_catalog(self):
        cart_object = self.env["purchase.order.line"]
        product_object = self.env["product.product"]
        cart_products_details = cart_object.search(
            [('order_id', "=", self.id)]) # , ("cart_flag", "=", True)
        if len(cart_products_details) > 0:
            for rec in cart_products_details:
                assign_quantity = rec.product_uom_qty
                rec.product_id._quantity = assign_quantity
        else:
            product_object_data = product_object.search(
                [("_quantity", "!=", 0)])
            for rec in product_object_data:
                rec._quantity = 0

        kanban_view = self.env.ref(
            'sttl_product_catalog_po.product_product_view_kanban_po')

        return {
            'type': 'ir.actions.act_window',
            'name': _('Choose Products'),
            'res_model': 'product.product',
            'views': [(kanban_view.id, 'kanban')],
            'context': {
                # '_quantity_change': True,
                'purchase_id': self.id
            },
            'help': _("""<p class="o_view_nocontent_smiling_face">
                            Create a new product
                        </p>""")
        }

    def pol_by_cart(self, operation, product_id, purchase_id):
        """
        Create Purchase Order Line By
        Cart Functionality
        """

        pol_object = self.env["purchase.order.line"]

        pol_data = dict()
        pol_data["product_id"] = product_id.id
        pol_data["order_id"] = purchase_id.id
        pol_data["price_unit"] = product_id.lst_price
        pol_data["product_uom"] = product_id.uom_id.id

        if operation == "add":
            pol_data["product_qty"] = product_id._quantity
            # pol_data["cart_flag"] = True
            pol_object.create(pol_data)
            return

        pol_ = pol_object.search(
            [('order_id', '=', purchase_id.id), ('product_id', '=', product_id.id)]) # , ("cart_flag", "=", True)

        if operation == "remove":
            if product_id._quantity <= 0:
                pol_.unlink()
                return
            pol_["product_qty"] = product_id._quantity

        elif operation == "update":
            pol_["product_qty"] = product_id._quantity
        return

    def user_input_qty_pol(self, _qty, product_id, purchase_id):
        pol_object = self.env["purchase.order.line"]
        product_object = self.env["product.product"]
        cart_product_details = pol_object.search(
            [('order_id', "=", purchase_id), ("product_id", "=", product_id)]) # ("cart_flag", "=", True)

        if len(cart_product_details) > 0:
            cart_product_details.product_qty = _qty
            cart_product_details.product_id._quantity = _qty
            if _qty == 0:
                cart_product_details.unlink()
            return
        else:
            if _qty == 0:
                return
            product_id = product_object.search([('id', '=', product_id)])
            pol_data = dict()
            pol_data["product_id"] = product_id.id
            pol_data["order_id"] = purchase_id
            pol_data["price_unit"] = product_id.lst_price
            pol_data["product_uom"] = product_id.uom_id.id
            pol_data["product_qty"] = _qty
            # pol_data["cart_flag"] = True
            po = pol_object.create(pol_data)
            po.product_id._quantity = _qty
            return
            

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    # cart_flag = fields.Boolean("Cart Flag", default=False)

    def unlink(self):
        self.product_id._quantity = 0
        return super().unlink()
