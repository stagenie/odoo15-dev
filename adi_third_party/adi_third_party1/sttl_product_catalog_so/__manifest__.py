# -*- coding: utf-8 -*-
{
    'name': 'Product Catalog for Sales Order',
    'version': '15.0.2.0',
    'author': 'Silver Touch Technologies Limited',
    'category': 'Sales',
    'summary': 'Allows adding and removing products to sales orders with a catalog interface.',
    'website': 'https://www.silvertouch.com/',
    'description': """
        This module enhances the sales order form by integrating a product catalog. 
        Users can easily add products to the sales order from a catalog view, 
        streamlining the order creation process.
    """,
    'depends': ['stock', 'product', 'sale_management'],
    'data': [
        'views/sale_order.xml',
        'views/product_product_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sttl_product_catalog_so/static/src/scss/product_product_views.scss',
            'sttl_product_catalog_so/static/src/js/product_product_views.js'
        ],
    },
    'currency': 'USD',
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'images': ['static/description/banner.png'],
}
