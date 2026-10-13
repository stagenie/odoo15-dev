# -*- coding: utf-8 -*-
{
    'name': "Vente - Alerte prix de vente inférieur au coût",
    'version': '15.0.1.0.0',
    'summary': "Avertit (sans bloquer) à la saisie d'une ligne de devis dont le prix "
               "net après remise est inférieur au coût du produit.",
    'description': """
Alerte prix de vente < coût sur les lignes de devis
===================================================

À la saisie ou modification d'une ligne de devis / commande (produit, prix
unitaire, remise, unité), si le prix net :

    prix net = prix unitaire HT x (1 - remise %)

est inférieur au coût unitaire de la ligne (champ « Coût » de sale_margin,
calculé depuis le coût du produit et converti dans l'unité de la ligne),
une fenêtre d'avertissement s'affiche. La saisie n'est pas bloquée.

Visibilité du coût (adi_hide_cost_margin) :
  - membres du groupe « Voir le Coût » : l'alerte affiche le coût, le prix net
    et la perte unitaire ;
  - autres utilisateurs : l'alerte s'affiche sans montant de coût.

Aucune alerte si le produit n'a pas de coût renseigné (coût = 0).
    """,
    'author': 'ADI',
    'category': 'Sales/Sales',
    'license': 'LGPL-3',
    'depends': [
        'sale_margin',
        'adi_hide_cost_margin',
    ],
    'data': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
