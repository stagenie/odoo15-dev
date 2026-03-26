# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    activite_required_for_invoice = fields.Boolean(
        string="Activit\u00e9 obligatoire pour l'impression",
        help="Exiger que l'activit\u00e9 du client soit renseign\u00e9e avant d'imprimer les factures",
        config_parameter='adi_partner_activite.activite_required_for_invoice',
        default=True,
    )
