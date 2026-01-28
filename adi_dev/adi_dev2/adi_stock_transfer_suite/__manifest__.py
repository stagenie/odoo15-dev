# -*- coding: utf-8 -*-
{
    'name': 'ADI Stock Transfer Suite - Gestion des Envois Partiels',
    'version': '15.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Gestion des envois partiels avec option de renvoi du reste',
    'description': """
ADI Stock Transfer Suite
========================

Ce module étend la gestion des transferts de stock pour permettre :

**Fonctionnalités principales:**

1. **Quantité Envoyée Modifiable**
   - La colonne "Qté Envoyée" est pré-remplie avec la quantité demandée à l'approbation
   - L'expéditeur peut modifier cette quantité avant l'envoi
   - Permet de gérer les cas où le stock disponible ne permet pas d'envoyer tout

2. **Gestion des Envois Partiels**
   - Calcul automatique de la "Qté Non Envoyée" (demandée - envoyée)
   - Après réception, si des quantités n'ont pas été envoyées, deux options :
     * Créer une nouvelle demande de transfert pour le reste
     * Clôturer sans renvoyer le reste

3. **Traçabilité Complète**
   - Lien entre le transfert original et le transfert de renvoi
   - Historique visible dans les deux sens (origine ↔ renvoi)
   - Smart buttons pour naviguer facilement entre les transferts liés

**Workflow:**
```
Demande → Approbation (qty_sent = quantity) → Modification qty_sent → Envoi → Réception
                                                                              ↓
                                                      [Si qty_not_sent > 0]
                                                              ↓
                                              ┌─────────────────────────────┐
                                              │  • Créer demande de renvoi  │
                                              │  • Clôturer sans renvoi     │
                                              └─────────────────────────────┘
```
    """,
    'author': 'ADI Dev',
    'website': '',
    'depends': [
        'adi_stock_transfer',
        'adi_stock_transfer_enhanced',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_transfer_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
