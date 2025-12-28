# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_date_sequence_control = fields.Boolean(
        string="Contrôle Date/Séquence Facturation",
        config_parameter='adi_invoice_date_sequence_control.enabled',
        help="Activer le contrôle de cohérence entre les dates et numéros "
             "séquentiels des factures clients et avoirs."
    )
    invoice_date_sequence_control_date = fields.Date(
        string="Date d'application",
        help="Date à partir de laquelle la contrainte s'applique. "
             "Les factures avec une date antérieure ne seront pas contrôlées."
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        date_str = ICP.get_param(
            'adi_invoice_date_sequence_control.application_date', False
        )
        if date_str:
            try:
                res['invoice_date_sequence_control_date'] = fields.Date.from_string(date_str)
            except (ValueError, TypeError):
                res['invoice_date_sequence_control_date'] = False
        else:
            res['invoice_date_sequence_control_date'] = False
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        date_value = self.invoice_date_sequence_control_date
        if date_value:
            ICP.set_param(
                'adi_invoice_date_sequence_control.application_date',
                fields.Date.to_string(date_value)
            )
        else:
            ICP.set_param(
                'adi_invoice_date_sequence_control.application_date',
                False
            )
