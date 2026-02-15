# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        IrConfigSudo = self.env['ir.config_parameter'].sudo()
        result['demo_banner_enabled'] = IrConfigSudo.get_param(
            'web.demo_banner_enabled', default='True') == 'True'
        result['demo_banner_text'] = IrConfigSudo.get_param(
            'web.demo_banner_text', default='\u26a0 BASE DEMO - Formation \u26a0')
        return result
