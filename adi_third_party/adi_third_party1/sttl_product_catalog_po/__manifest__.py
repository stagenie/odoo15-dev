# -*- coding: utf-8 -*-
{
    "name": "Product Catalog For Purchase Order",
    "version": "15.0.2.0",
    "author": "Silver Touch Technologies Limited",
    'category': 'stock',
    "summary": "This module provides functionality of adding and removing product to cart in Purchase Order.",
    "website": "https://www.silvertouch.com/",
    "description": """
            This module is used to add product like add cart functionality
            to purchase order form view on button click product catalog button
            also select products and create this products po line of purchase order
            from tree view products.
        """,
    'depends': ['stock', 'purchase', 'product'],
    'data': [
        'views/purchase_order.xml',
        'views/product_product_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sttl_product_catalog_po/static/src/scss/product_product_views.scss',
            'sttl_product_catalog_po/static/src/js/product_product_views.js'
        ],
    },
    "price": 0,
    "currency": "USD",
    "license": "LGPL-3",
    'installable': True,
    'application': True,
    'images': ['static/description/banner.png'],
}
