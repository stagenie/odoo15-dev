from odoo import api, models, fields, _


class Product(models.Model):
    _inherit = "product.product"

    _quantity = fields.Float(default=0, store=True)

    def utilizable_cart_details(self):
        """
        Utilizable Cart Details For Remove , Add And Update Operations
        For Cart To Product Catelog Module To Object addcart.sales.products
        """

        context = self._context.copy() or {}
        cart_object = self.env["sale.order.line"]
        cart_details = dict()
        total_count = cart_object.search_count(
            [('product_id', '=', self.id), ('order_id', '=', context.get('sale_id'))]) # , ("cart_flag", "=", True)
        cart_details["total_count"] = total_count
        cart_data = cart_object.search(
            [('product_id', '=', self.id), ('order_id', '=', context.get('sale_id'))]) # , ("cart_flag", "=", True)
        cart_details["cart_data"] = cart_data
        return cart_details

    def initiate_sol(self, operation, sale_id):
        """
        Initiate Sale Order Line By Cart Functionality.
        """

        so_object = self.env["sale.order"]
        sale_object = so_object.search([("id", "=", sale_id)])
        if operation == "add":
            so_object.sol_by_cart(operation, self, sale_object)
        elif operation == "remove":
            so_object.sol_by_cart(operation, self, sale_object)
        elif operation == "update":
            so_object.sol_by_cart(operation, self, sale_object)

    def set_quantity_so(self, quantity, operation=None):
        context = self._context.copy() or {}
        cart_details = self.utilizable_cart_details()
        if operation == "remove":
            self._quantity -= quantity
            if cart_details.get("total_count") != 0:
                self.initiate_sol("remove", context.get("sale_id"))
        else:
            self._quantity += quantity
            if cart_details.get("total_count") != 0:
                self.initiate_sol("update", context.get("sale_id"))
            else:
                self.initiate_sol("add", context.get("sale_id"))

    def remove_quantity_button_so(self):
        if self._quantity == 0:
            self._quantity = 0
            return
        return self.set_quantity_so(1, operation="remove")

    def add_quantity_button_so(self):
        return self.set_quantity_so(1, operation="add")
