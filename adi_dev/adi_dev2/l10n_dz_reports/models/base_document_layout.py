# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    rc = fields.Char(related='company_id.rc', readonly=True)
    rc = fields.Char(related='company_id.rc', readonly=True)
    nis = fields.Char(related='company_id.nis', readonly=True)
    nif = fields.Char(related='company_id.nif', readonly=True)
    ai = fields.Char(related='company_id.ai', readonly=True)

    fax = fields.Char(related='company_id.fax', readonly=True)
    street = fields.Char(related='company_id.street', readonly=True)
    street2 = fields.Char(related='company_id.street2', readonly=True)
    zip = fields.Char(related='company_id.zip', readonly=True)
    city = fields.Char(related='company_id.city', readonly=True)
    state_id = fields.Many2one(related='company_id.state_id', readonly=True)

    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    capital_social = fields.Monetary(related='company_id.capital_social', readonly=True)
    forme_juridique = fields.Many2one(related='company_id.forme_juridique', readonly=True)