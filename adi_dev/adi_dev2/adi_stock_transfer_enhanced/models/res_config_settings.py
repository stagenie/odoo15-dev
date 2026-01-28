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

    # === Configuration Désactivation des Reliquats ===
    transfer_disable_backorder = fields.Boolean(
        string="Désactiver les reliquats",
        help="Si activé, les transferts n'autorisent plus les réceptions partielles. "
             "Les quantités approuvées sont envoyées et reçues en totalité. "
             "En cas d'écart, les deux parties font un ajustement manuel.",
        config_parameter='adi_stock_transfer_enhanced.disable_backorder'
    )
