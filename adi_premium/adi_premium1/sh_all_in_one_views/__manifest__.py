# -*- coding: utf-8 -*-
{
    "name": "Toutes les Vues de Lignes",
    "author": "Softhealer Technologies",
    "license": "OPL-1",
    "website": "https://www.softhealer.com",
    "version": "15.0.1",
    "category": "Outils Supplémentaires",
    "summary": """
Afficher les Lignes de Réception, Afficher les Lignes de Livraison,
Afficher les Lignes de Bon de Commande d'Achat, Afficher les Lignes de Demande de Prix,
Afficher les Lignes de Devis, Afficher les Lignes de Commande de Vente
""",
    "description": """
Ce module permet d'afficher les lignes de commande de vente/devis,
commande d'achat/demande de prix, réceptions/livraisons,
factures/avoirs clients et fournisseurs
ainsi que les informations relatives aux produits
en utilisant les options de filtre et de regroupement.
Vous pouvez facilement ajouter des filtres/groupes personnalisés pour
les lignes de commande de vente/devis/commande d'achat/demande de prix/
réceptions/livraisons/factures/avoirs.
Travaillez facilement avec les lignes directement via
les vues liste, formulaire, kanban, recherche, pivot, graphique et calendrier.
""",
    "depends": ["sale_management", "account", "purchase", "stock"],
    "data": [
        "views/account_invoice_line.xml",
        "views/purchase_order_line.xml",
        "views/sale_order_line.xml",
        "views/stock_view.xml",
    ],
    "images": ["static/description/background.png", ],
    "live_test_url": "https://youtu.be/LjAyw4WuXqw",
    "auto_install": False,
    "installable": True,
    "application": True,
    "price": 40,
    "currency": "EUR"
}
