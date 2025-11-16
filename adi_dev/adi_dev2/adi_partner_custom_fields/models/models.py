from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    point_de_vente = fields.Char(string="Point de Vente")
    forme_juridique = fields.Char(string="Forme Juridique")
    date_creation = fields.Datetime(string="Date création", default=fields.Datetime.now)