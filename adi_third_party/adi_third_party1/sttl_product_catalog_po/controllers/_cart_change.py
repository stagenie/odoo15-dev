from odoo import http
import json


class QtyChangePO(http.Controller):

    @http.route(['/qtyupdatecart_po'], type='http', auth='public', website=True)
    def QtyUpdatePO(self, **post):
        _pol_obj = http.request.env["purchase.order"]
        _pol_obj.user_input_qty_pol(
            float(post.get("quantity")), int(post.get("product_id")), int(post.get("purchase_id")))
        return json.dumps({"message": True})

    # @http.route(['/getuom_po'], type='http', auth='user', website=True)
    # def UOMGetPO(self, **post):
    #     product = http.request.env['product.product'].search([('id', '=', post["product_id"])])
    #     uom_category = product.product_tmpl_id.uom_id.category_id.name
    #     return json.dumps({"uom_category": uom_category.lower()})
