{
    'name': 'Adi Partner Credit Limit',
    'version': '15.0.0.0',
    'sequence': 1,
    'category': 'Sales',
    'summary': 'Adi Partner Limit  . ',
    'description': "ADI partner Limit. ",
    "author" : "ADICOPS",
    "email": 'info@adicops.com',
    "website":'https://adicops.com/',
    'license': 'AGPL-3',
    'depends': [
        'sale',
        'account',
        'accounting_pdf_reports',  # Pour la cohérence avec le rapport Partner Ledger
        'adi_partner_ledger_exclude',  # Pour le champ exclude_from_partner_ledger
    ], 
    "data":  [
       # 'security/ir.model.access.csv',
       # 'views/product.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        ],
    'demo': [],
    'test': [],
    'qweb': [],    
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
