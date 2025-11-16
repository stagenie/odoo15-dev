{
    'name': 'Adi partner custom fields',
    'version': '15.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Ajoute les dimensions aux lignes de commande et facture',
    'description': """
        Ajoute les dimensions aux lignes de commande et facture',
    """,
    'depends': ['sale', 'account'],
    'data': [
        'views/views.xml',
       
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}