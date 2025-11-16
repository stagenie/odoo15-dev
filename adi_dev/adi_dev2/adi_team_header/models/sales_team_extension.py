from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    activity_description = fields.Text(
        string="Description de l'activité",
        help="Description détaillée de l'activité principale de la société",
        translate=True  # Optionnel : permet la traduction
    )

class SalesTeamExtension(models.Model):
    _inherit = 'crm.team'

    team_address = fields.Char(string='Team Address')
    rc = fields.Char(string='RC:')
    nif = fields.Char(string='NIF:')
    ai = fields.Char(string='AI:')
    nis = fields.Char(string='NIS: ')    
    team_address = fields.Char(string='Adresse')
    email = fields.Char(string='Email(s):')
    tel = fields.Char(string='N°(s) Tel:')
    team_description = fields.Text(string='Description')