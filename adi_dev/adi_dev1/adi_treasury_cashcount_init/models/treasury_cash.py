# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class TreasuryCash(models.Model):
    _inherit = 'treasury.cash'

    # =============================================
    # COMPTAGE INITIAL
    # =============================================

    enable_initial_count = fields.Boolean(
        string='Activer le comptage initial',
        default=False,
        help="Si coché, le comptage initial sera disponible pour vérifier "
             "le solde de départ lors de l'ouverture des clôtures."
    )

    force_initial_count = fields.Boolean(
        string='Forcer le comptage initial',
        default=False,
        help="Si coché, le comptage initial des billets et pièces sera obligatoire "
             "lors de la confirmation des clôtures de cette caisse.\n\n"
             "L'utilisateur devra effectuer le comptage initial avant de confirmer."
    )
