from odoo import http
import json


class QtyChangeSO(http.Controller):

    @http.route(['/qtyupdatecart_so'], type='http', auth='user', website=True)
    def QtyUpdateSO(self, **post):
        _sol_obj = http.request.env["sale.order"]
        _sol_obj.user_input_qty_sol(
            float(post.get("quantity")), int(post.get("product_id")), int(post.get("sale_id")))
        return json.dumps({"message": True})

    # @http.route(['/getuom_so'], type='http', auth='user', website=True)
    # def UOMGetSO(self, **post):
    #     product = http.request.env['product.product'].search([('id', '=', post["product_id"])])
    #     uom_category = product.product_tmpl_id.uom_id.category_id.name
    #     return json.dumps({"uom_category": uom_category.lower()})
