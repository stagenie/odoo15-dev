from odoo import models, fields, _


class Product(models.Model):
    _inherit = "product.product"

    _quantity = fields.Float(default=0, store=True)

    def utilizable_cart_details_po(self):
        """
        Utilizable Cart Details For Remove , Add And Update Operations
        For Cart To Product Catalog Module To Object addcart.purchase.products
        """

        context = self._context.copy() or {}
        cart_object = self.env["purchase.order.line"]
        cart_details = dict()
        total_count = cart_object.search_count(
            [('product_id', '=', self.id), ('order_id', '=', context.get('purchase_id'))]) # , ("cart_flag", "=", True)
        cart_details["total_count"] = total_count
        cart_data = cart_object.search(
            [('product_id', '=', self.id), ('order_id', '=', context.get('purchase_id'))]) # , ("cart_flag", "=", True)
        cart_details["cart_data"] = cart_data
        return cart_details

    def initiate_pol(self, operation, purchase_id):
        """
        Initiate Purchase Order Line By Cart Functionality.
        """

        po_object = self.env["purchase.order"]
        purchase_object = po_object.search([("id", "=", purchase_id)])
        if operation == "add":
            po_object.pol_by_cart(operation, self, purchase_object)
        elif operation == "remove":
            po_object.pol_by_cart(operation, self, purchase_object)
        elif operation == "update":
            po_object.pol_by_cart(operation, self, purchase_object)

    def set_quantity_po(self, quantity, operation=None):
        context = self._context.copy() or {}
        cart_details = self.utilizable_cart_details_po()
        if operation == "remove":
            self._quantity -= quantity
            if cart_details.get("total_count") != 0:
                self.initiate_pol("remove", context.get("purchase_id"))
        else:
            self._quantity += quantity
            if cart_details.get("total_count") != 0:
                self.initiate_pol("update", context.get("purchase_id"))
            else:
                self.initiate_pol("add", context.get("purchase_id"))

    def remove_quantity_button_po(self):
        if self._quantity == 0:
            self._quantity = 0
            return
        return self.set_quantity_po(1, operation="remove")

    def add_quantity_button_po(self):
        return self.set_quantity_po(1, operation="add")
