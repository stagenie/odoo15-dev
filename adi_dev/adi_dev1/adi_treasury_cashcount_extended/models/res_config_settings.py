# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # =============================================
    # COMPTAGE FINAL
    # =============================================

    force_cash_count_global = fields.Boolean(
        string='Forcer le comptage final (Global)',
        config_parameter='adi_treasury_cashcount_extended.force_cash_count',
        help="Si coché, le comptage des billets et pièces sera obligatoire "
             "pour TOUTES les caisses lors de la confirmation des clôtures.\n\n"
             "Cette option est prioritaire sur le paramètre individuel de chaque caisse."
    )

    # =============================================
    # AFFICHAGE DANS LES RAPPORTS
    # =============================================

    hide_count_in_report_global = fields.Boolean(
        string='Masquer le comptage dans les rapports (Global)',
        config_parameter='adi_treasury_cashcount_extended.hide_count_in_report',
        help="Si coché, le détail du comptage des billets et pièces sera masqué "
             "dans TOUS les rapports de clôture de caisse.\n\n"
             "Seuls les totaux seront affichés."
    )
