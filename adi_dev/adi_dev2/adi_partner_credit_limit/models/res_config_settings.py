# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    partner_balance_mode = fields.Selection(
        selection=[
            ('receivable', 'Solde client uniquement (Receivable)'),
            ('net', 'Solde net (Receivable + Payable)'),
        ],
        string="Mode de calcul du solde partenaire",
        config_parameter='adi_partner_credit_limit.partner_balance_mode',
        default='receivable',
        help="Choisissez comment calculer le solde affiché dans le formulaire contact:\n"
             "- Solde client uniquement: Affiche uniquement les créances (comptes receivable)\n"
             "- Solde net: Affiche le solde net incluant créances et dettes (receivable + payable)"
    )
