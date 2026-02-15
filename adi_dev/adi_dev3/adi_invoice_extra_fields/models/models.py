from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    purchase_order_number = fields.Char(string='N° Bon de Commande')
    contract_number = fields.Char(string='N° de Contrat')
    delivery_note_number = fields.Char(string='BL N°')
    invoice_object = fields.Text(string='Objet')