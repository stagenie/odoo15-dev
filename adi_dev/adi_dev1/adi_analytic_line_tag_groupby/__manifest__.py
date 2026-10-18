{
    'name': 'Lignes analytiques — Regroupement par étiquette',
    'category': 'Accounting',
    'version': '15.0.1.0',
    'summary': 'Regrouper, filtrer et afficher les lignes analytiques par étiquette analytique',
    'description': """
Besoin
------
Voir les frais d'un projet par catégorie de dépense (CHANTIER, FINITION,
Électricité...) portée par les étiquettes analytiques.

Ajouts sur les lignes analytiques (liste, pivot, graphique)
------------------------------------------------------------
* Regroupement « Étiquette analytique » (many2many : une ligne portant deux
  étiquettes apparaît dans les deux groupes).
* Filtres « Avec étiquette » / « Sans étiquette ».
* Recherche par étiquette déjà disponible (champ Tags du module analytic).
* Colonne Étiquettes affichée par défaut dans la liste.
""",
    'author': 'ADICOPS',
    'email': 'info@adicops.com',
    'website': 'https://adicops.com/',
    'license': 'AGPL-3',
    'depends': ['analytic'],
    'data': [
        'views/account_analytic_line_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
