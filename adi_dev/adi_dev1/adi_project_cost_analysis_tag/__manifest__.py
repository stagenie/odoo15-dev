{
    'name': 'Analyse des Coûts Projets — par Dépense (étiquette)',
    'category': 'Project',
    'version': '15.0.1.0',
    'summary': 'Wizard supplémentaire : coûts projet regroupés par catégorie de dépense (étiquette analytique)',
    'description': """
Ajoute un second wizard « Analyse des Coûts par Dépense » à côté du wizard
existant « Analyse des Coûts Projets » (inchangé).

Mêmes filtres que le wizard existant (projets, articles, période) plus :

* filtre sur une ou plusieurs étiquettes analytiques ;
* inclusion ou non des dépenses sans étiquette ;
* détail par article dans chaque catégorie (optionnel).

Rapport : Projet → récapitulatif par catégorie (montant, %) → détail des
articles par catégorie.

Source : mêmes lignes que le wizard existant (factures et avoirs fournisseurs
comptabilisés, lignes avec compte analytique et article), donc mêmes totaux.
L'étiquette est lue sur la ligne de facture et sur ses lignes analytiques
(une étiquette posée directement depuis les écritures analytiques est prise
en compte). Une ligne portant plusieurs étiquettes est classée dans la
catégorie combinée « A + B » pour ne pas être comptée deux fois.
""",
    'author': 'ADICOPS',
    'email': 'info@adicops.com',
    'website': 'https://adicops.com/',
    'license': 'AGPL-3',
    'depends': [
        'adi_project_cost_analysis',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/project_cost_analysis_tag_report.xml',
        'views/wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
