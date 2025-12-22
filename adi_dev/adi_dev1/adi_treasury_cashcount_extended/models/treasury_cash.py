# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class TreasuryCash(models.Model):
    _inherit = 'treasury.cash'

    # =============================================
    # COMPTAGE FINAL
    # =============================================

    force_cash_count = fields.Boolean(
        string='Forcer le comptage final',
        default=False,
        help="Si coché, le comptage des billets et pièces sera obligatoire "
             "lors de la confirmation des clôtures de cette caisse.\n\n"
             "L'utilisateur devra utiliser le wizard de comptage pour saisir "
             "le solde réel."
    )

    # =============================================
    # AFFICHAGE DANS LES RAPPORTS
    # =============================================

    show_count_in_report = fields.Boolean(
        string='Afficher le comptage dans les rapports',
        default=True,
        help="Si coché, le détail du comptage des billets et pièces sera "
             "affiché dans le rapport de clôture de caisse.\n\n"
             "Si décoché, seuls les totaux seront affichés."
    )
