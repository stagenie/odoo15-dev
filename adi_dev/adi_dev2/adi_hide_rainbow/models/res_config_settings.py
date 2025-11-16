from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    disable_rainbow_man = fields.Boolean(string="Désactiver le Rainbow Man", config_parameter='adi_hide_rainbow.disable')