# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    return_origin_mode = fields.Selection([
        ('none', 'Libre - Tous les produits'),
        ('flexible', 'Souple - Produits deja livres au client'),
        ('strict', 'Strict - Commandes et BL specifiques'),
    ],
        string="Mode de selection des produits",
        help="""
        - Libre : L'utilisateur peut selectionner n'importe quel produit stockable
        - Souple : Seuls les produits deja livres au client peuvent etre retournes
        - Strict : L'utilisateur doit selectionner les commandes et BL d'origine,
          seuls les produits de ces BL peuvent etre retournes
        """,
        config_parameter='adi_return_management.return_origin_mode',
        default='none'
    )

    return_check_qty_exceeded = fields.Boolean(
        string="Controler quantite retournee",
        help="Si active, empeche le retour d'une quantite superieure a la quantite livree",
        config_parameter='adi_return_management.return_check_qty_exceeded',
        default=True
    )
