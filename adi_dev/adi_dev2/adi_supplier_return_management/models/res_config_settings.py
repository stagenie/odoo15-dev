# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    supplier_return_origin_mode = fields.Selection([
        ('none', 'Libre - Tous les produits'),
        ('flexible', 'Souple - Produits deja recus du fournisseur'),
        ('strict', 'Strict - Produits d\'une commande/BR specifique'),
    ],
        string='Mode origine retour fournisseur',
        config_parameter='adi_supplier_return_management.return_origin_mode',
        default='none',
        help="""
        Definit comment les produits peuvent etre selectionnes dans un retour fournisseur:
        - Libre: Tous les produits stockables peuvent etre retournes
        - Souple: Seuls les produits deja recus de ce fournisseur
        - Strict: Produits d'une commande achat / bon de reception specifique
        """
    )

    supplier_return_check_qty_exceeded = fields.Boolean(
        string="Controler quantite retournee",
        help="Si active, empeche le retour d'une quantite superieure a la quantite recue",
        config_parameter='adi_supplier_return_management.return_check_qty_exceeded',
        default=True
    )
