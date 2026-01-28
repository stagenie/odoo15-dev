# -*- coding: utf-8 -*-
{
    'name': 'WhatsApp Send Documents',
    'version': '15.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Envoyer les documents commerciaux via WhatsApp',
    'description': """
        Module pour envoyer les documents commerciaux via WhatsApp :
        - Devis et Bons de commande clients
        - Factures clients
        - Demandes de prix et Bons de commande fournisseurs

        Fonctionnalités :
        - Configuration des rapports PDF par type de document
        - Templates de messages personnalisables
        - Envoi via lien WhatsApp (wa.me)
        - Historique des envois dans le chatter
    """,
    'author': 'ADICOPS',
    'website': 'https://www.adicops.com',
    'depends': [
        'sale',
        'purchase',
        'account',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/whatsapp_document_type_data.xml',
        'views/whatsapp_document_config_views.xml',
        'views/whatsapp_message_template_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/purchase_order_views.xml',
        'wizard/whatsapp_send_wizard_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
