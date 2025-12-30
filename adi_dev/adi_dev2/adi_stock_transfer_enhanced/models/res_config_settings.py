# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # === Configuration Restriction par Équipe ===
    transfer_restrict_by_team = fields.Boolean(
        string="Restreindre les opérations par équipe",
        help="Si activé, seuls les membres de l'équipe source peuvent envoyer "
             "et seuls les membres de l'équipe destination peuvent réceptionner.",
        config_parameter='adi_stock_transfer_enhanced.restrict_by_team'
    )

    transfer_team_required = fields.Boolean(
        string="Équipes obligatoires",
        help="Si activé, les champs équipe source et destination sont obligatoires.",
        config_parameter='adi_stock_transfer_enhanced.team_required'
    )
