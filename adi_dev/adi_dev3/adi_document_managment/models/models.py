# models/document.py
from odoo import models, fields, api

class DocumentDocument(models.Model):
    _name = 'document.document'
    _description = 'Administrative Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nom du document', required=True)
    category_id = fields.Many2one('document.category', string='Catégorie')
    tag_ids = fields.Many2many('document.tag', string='Étiquettes (Tags)')
    description = fields.Html(string='Description')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Partenaire')


    def action_draft(self):
        self.state = 'draft'

    def action_in_progress(self):
        self.state = 'in_progress'

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'

    def action_reset_to_draft(self):
        self.state = 'draft'


    priority = fields.Selection([
        ('0', 'Basse'),
        ('1', 'Moyenne'),
        ('2', 'Elevée')], default='1', string='Priorité')
    
    state = fields.Selection([
        ('draft', 'Brouilon'),
        ('in_progress', 'En progression'), 
        ('done', 'Fait'),
        ('cancel', 'Annulé')], default='draft', string='Etat',tracking=True)

    @api.depends('state')   
    def _compute_state_color(self):
        for doc in self:
            if doc.state == 'draft':
                doc.state_color = 1  # Gris
            elif doc.state == 'in_progress':
                doc.state_color = 4  # Bleu
            elif doc.state == 'done':
                doc.state_color = 10  # Vert
            else:
                doc.state_color = 9  # Rouge
                
    state_color = fields.Integer(compute='_compute_state_color')

    
 
class DocumentCategory(models.Model):
    _name = 'document.category'
    _description = 'Document Category'

    name = fields.Char(string='Nom de catégorie', required=True)
    parent_id = fields.Many2one('document.category', string='Catégorie Mère')

 
class DocumentTag(models.Model):  
    _name = 'document.tag'
    _description = 'Document Tag'

    name = fields.Char(string="Nom de l'Étiquettes", required=True) 
    color = fields.Integer(string='Colour')