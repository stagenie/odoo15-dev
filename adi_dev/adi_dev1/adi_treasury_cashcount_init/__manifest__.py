# -*- coding: utf-8 -*-
{
    'name': 'Comptage Initial de Caisse',
    'version': '15.0.1.0.0',
    'category': 'Accounting/Treasury',
    'summary': 'Comptage initial pour vérifier le solde de départ des clôtures de caisse',
    'description': """
Comptage Initial de Caisse
==========================

Ce module ajoute la fonctionnalité de comptage initial aux clôtures de caisse.

**Fonctionnalités:**

1. **Comptage Initial**
   - Vérification du solde de départ lors de l'ouverture de la clôture
   - Onglet "Comptage Initial" avec détail des billets/pièces
   - Option "Activer le comptage initial" (par caisse ou global)
   - Option "Forcer le comptage initial" (par caisse ou global)
   - Détection des écarts dès l'ouverture de la clôture

2. **Wizard de Comptage Initial**
   - Interface intuitive avec onglets Billets / Pièces / Tout
   - Calcul automatique du total en temps réel
   - Affichage de l'écart avec le solde de départ théorique

3. **Solde de départ ajusté**
   - Si un écart initial est détecté, le solde initial compté est utilisé
     comme base pour le calcul du solde théorique final
   - Formule: Solde théorique = Solde ajusté + Entrées - Sorties

4. **Configuration flexible**
   - Options configurables par caisse ou globalement
   - Paramètres dans Comptabilité > Configuration > Paramètres

5. **Rapports**
   - Colonnes comptage initial dans la vue liste
   - Intégration au rapport de clôture de caisse
    """,
    'author': 'ADI Dev',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'adi_treasury_cashcount_extended',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/initial_cash_count_wizard_views.xml',
        'views/treasury_cash_closing_views.xml',
        'views/treasury_cash_views.xml',
        'views/res_config_settings_views.xml',
        'reports/treasury_cash_closing_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
