# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WhatsappDocumentConfig(models.Model):
    _name = 'whatsapp.document.config'
    _description = 'Configuration WhatsApp par type de document'
    _order = 'sequence, id'

    name = fields.Char(
        string='Nom',
        required=True,
        help="Nom du type de document (ex: Devis Client, Facture, etc.)"
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Type de document
    document_type = fields.Selection([
        ('sale_quotation', 'Devis Client'),
        ('sale_order', 'Bon de Commande Client'),
        ('invoice', 'Facture Client'),
        ('credit_note', 'Avoir Client'),
        ('purchase_rfq', 'Demande de Prix Fournisseur'),
        ('purchase_order', 'Bon de Commande Fournisseur'),
    ], string='Type de Document', required=True)

    # Modèle Odoo associé (calculé automatiquement)
    model_name = fields.Char(
        string='Modèle',
        compute='_compute_model_name',
        store=True
    )

    # Rapports PDF à envoyer (Many2many filtré par modèle)
    report_ids = fields.Many2many(
        'ir.actions.report',
        'whatsapp_config_report_rel',
        'config_id',
        'report_id',
        string='Rapports PDF à envoyer',
        help="Sélectionnez les rapports PDF qui seront joints lors de l'envoi WhatsApp"
    )

    # Template de message par défaut
    template_id = fields.Many2one(
        'whatsapp.message.template',
        string='Template de Message',
        help="Template de message par défaut pour ce type de document"
    )

    # Champ pour le numéro de téléphone
    phone_field = fields.Selection([
        ('mobile', 'Mobile'),
        ('phone', 'Téléphone'),
    ], string='Champ Téléphone', default='mobile',
       help="Champ à utiliser pour récupérer le numéro WhatsApp du partenaire")

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        default=lambda self: self.env.company
    )

    @api.depends('document_type')
    def _compute_model_name(self):
        """Calcule le modèle Odoo en fonction du type de document"""
        type_to_model = {
            'sale_quotation': 'sale.order',
            'sale_order': 'sale.order',
            'invoice': 'account.move',
            'credit_note': 'account.move',
            'purchase_rfq': 'purchase.order',
            'purchase_order': 'purchase.order',
        }
        for record in self:
            record.model_name = type_to_model.get(record.document_type, '')

    @api.onchange('document_type')
    def _onchange_document_type(self):
        """Réinitialise les rapports quand le type change et retourne le domaine"""
        self.report_ids = [(5, 0, 0)]
        if self.document_type:
            return {
                'domain': {
                    'report_ids': [('model', '=', self.model_name)]
                }
            }
        return {}

    @api.constrains('document_type', 'company_id')
    def _check_unique_config(self):
        """Vérifie qu'il n'y a qu'une seule configuration active par type et société"""
        for record in self:
            if record.active:
                existing = self.search([
                    ('document_type', '=', record.document_type),
                    ('company_id', '=', record.company_id.id),
                    ('active', '=', True),
                    ('id', '!=', record.id),
                ])
                if existing:
                    raise ValidationError(_(
                        "Une configuration active existe déjà pour le type '%s' dans cette société."
                    ) % dict(self._fields['document_type'].selection).get(record.document_type))

    @api.model
    def get_config_for_document(self, document_type, company_id=None):
        """Récupère la configuration pour un type de document donné"""
        domain = [
            ('document_type', '=', document_type),
            ('active', '=', True),
        ]
        if company_id:
            domain.append(('company_id', 'in', [company_id, False]))

        config = self.search(domain, limit=1, order='company_id desc')
        return config

    def get_available_reports(self):
        """Retourne les rapports disponibles pour ce type de document"""
        self.ensure_one()
        return self.env['ir.actions.report'].search([
            ('model', '=', self.model_name)
        ])
