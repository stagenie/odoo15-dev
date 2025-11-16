from odoo import api, models,fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    detailed_type = fields.Selection([
        ('product', 'Stockable'),
        ('consu', 'Consommable'),        
        ('service', 'Service')], string='Product Type', default='product', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')
        
        
"""
    @api.model
    def create(self, values):
        if 'type' not in values:
            values['type'] = 'product'  # Change to 'consu' or 'service' if needed

        return super(ProductTemplate, self).create(values)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    is_product_type_set = fields.Boolean(string="Product Type Set", default=False)
       
    @api.model
    def create(self, values):
        if 'product_id' in values and not values.get('is_product_type_set'):
            product = self.env['product.product'].browse(values['product_id'])
            if product:
                product.type = 'product'  # Change to 'consu' or 'service' if needed

        return super(PurchaseOrderLine, self).create(values)
    
"""  