from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_limit_active = fields.Boolean(
        string="Activer la limite de crédit",
        default=False
    )
    credit_limit = fields.Float(
        string="Limite de crédit",
        help="Montant maximum autorisé pour ce client."
    )
