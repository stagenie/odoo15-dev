# -*- coding: utf-8 -*-
{
    'name': 'Costing Projet - Calcul Devis avec Marges',
    'version': '15.0.1.0.0',
    'category': 'Sales',
    'sequence': 15,
    'summary': 'Calcul de prix de vente à partir du coût avec marges équipement et main d\'oeuvre',
    'description': """
Module de Calcul Costing Projet
===============================

Fonctionnalités :
-----------------
* Calcul du prix de vente : Coût × (1 + %Équipement + %M.O.)
* Prix d'achat basé sur le coût standard produit (standard_price)
* Saisie manuelle des pourcentages de marge
* Wizard de saisie rapide avec marges par défaut
* Smart Button sur les devis pour accéder aux calculs
* Synchronisation automatique vers les lignes de devis
* Modifiable uniquement en état Devis (draft/sent)
* Traçabilité complète (état de synchronisation, dates)

Workflow :
----------
1. Créer un devis
2. Cliquer sur "Calcul Costing" pour ouvrir le wizard
3. Ajouter les produits avec leurs % de marge
4. Valider pour créer les lignes de costing
5. Synchroniser vers les lignes du devis
6. Le devis final affiche uniquement le prix de vente calculé
    """,
    'author': 'ADICOPS',
    'website': 'https://adicops-dz.com',
    'license': 'LGPL-3',
    'depends': [
        'sale_management',
        'product',
    ],
    'data': [
        # Sécurité (en premier)
        'security/project_costing_security.xml',
        'security/ir.model.access.csv',
        # Vues
        'views/project_costing_line_views.xml',
        'views/sale_order_views.xml',
        'views/wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
