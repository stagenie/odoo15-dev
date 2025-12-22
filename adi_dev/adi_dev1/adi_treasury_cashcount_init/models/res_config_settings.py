# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # =============================================
    # COMPTAGE INITIAL
    # =============================================

    enable_initial_count_global = fields.Boolean(
        string='Activer le comptage initial (Global)',
        config_parameter='adi_treasury_cashcount_init.enable_initial_count',
        help="Si coché, le comptage initial sera disponible pour TOUTES les caisses "
             "pour vérifier le solde de départ lors de l'ouverture des clôtures."
    )

    force_initial_count_global = fields.Boolean(
        string='Forcer le comptage initial (Global)',
        config_parameter='adi_treasury_cashcount_init.force_initial_count',
        help="Si coché, le comptage initial des billets et pièces sera obligatoire "
             "pour TOUTES les caisses lors de la confirmation des clôtures.\n\n"
             "Cette option est prioritaire sur le paramètre individuel de chaque caisse."
    )
