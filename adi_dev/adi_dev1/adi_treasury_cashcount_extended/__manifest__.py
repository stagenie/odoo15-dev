# -*- coding: utf-8 -*-
{
    'name': 'Comptage Caisse Étendu',
    'version': '15.0.2.0.0',
    'category': 'Accounting/Treasury',
    'summary': 'Extension du comptage de caisse avec wizard et option de forçage',
    'description': """
Comptage Caisse Étendu
======================

Ce module étend le module de comptage de caisse (adi_treasury_cashcount) avec les fonctionnalités suivantes:

**Fonctionnalités:**

1. **Comptage Final (amélioré)**
   - Onglet "Comptage" en lecture seule
   - Wizard dédié pour le comptage des billets et pièces
   - Option "Forcer le comptage" (par caisse ou global)

2. **Wizard de Comptage**
   - Interface intuitive avec onglets Billets / Pièces / Tout
   - Calcul automatique du total en temps réel
   - Affichage de l'écart avec le solde théorique

3. **Configuration flexible**
   - Options configurables par caisse ou globalement
   - Paramètres dans Comptabilité > Configuration > Paramètres

4. **Rapports**
   - Intégration du détail du comptage au rapport de clôture
   - Option pour masquer le détail du comptage dans les rapports
    """,
    'author': 'ADI Dev',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'adi_treasury_cashcount',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/cash_count_wizard_views.xml',
        'views/treasury_cash_closing_views.xml',
        'views/treasury_cash_views.xml',
        'views/res_config_settings_views.xml',
        'reports/treasury_cash_closing_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
