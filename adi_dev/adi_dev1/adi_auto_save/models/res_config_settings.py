# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auto_save_enabled = fields.Boolean(
        string='Activer l\'enregistrement automatique',
        default=True,
        config_parameter='adi_auto_save.auto_save_enabled',
        help="Active l'enregistrement automatique pour les devis/commandes et les achats"
    )

    auto_save_interval = fields.Integer(
        string='Intervalle de sauvegarde (secondes)',
        default=30,
        config_parameter='adi_auto_save.auto_save_interval',
        help="Temps en secondes entre chaque sauvegarde automatique"
    )

    auto_save_sale_order = fields.Boolean(
        string='Devis/Bons de commandes',
        default=True,
        config_parameter='adi_auto_save.auto_save_sale_order',
        help="Activer l'auto-save pour les devis et bons de commandes"
    )

    auto_save_purchase_order = fields.Boolean(
        string='Demandes/Commandes d\'achat',
        default=True,
        config_parameter='adi_auto_save.auto_save_purchase_order',
        help="Activer l'auto-save pour les demandes et commandes d'achat"
    )
