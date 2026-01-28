# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import re


class WhatsappMessageTemplate(models.Model):
    _name = 'whatsapp.message.template'
    _description = 'Template de message WhatsApp'
    _order = 'name'

    name = fields.Char(
        string='Nom du Template',
        required=True
    )
    active = fields.Boolean(default=True)

    # Type de document concerné
    document_type = fields.Selection([
        ('sale_quotation', 'Devis Client'),
        ('sale_order', 'Bon de Commande Client'),
        ('invoice', 'Facture Client'),
        ('credit_note', 'Avoir Client'),
        ('purchase_rfq', 'Demande de Prix Fournisseur'),
        ('purchase_order', 'Bon de Commande Fournisseur'),
        ('all', 'Tous les documents'),
    ], string='Type de Document', default='all', required=True)

    # Contenu du message
    body = fields.Text(
        string='Contenu du Message',
        required=True,
        help="""Utilisez les placeholders suivants :
        {{partner_name}} - Nom du partenaire
        {{document_name}} - Référence du document
        {{document_date}} - Date du document
        {{amount_total}} - Montant total
        {{currency}} - Devise
        {{company_name}} - Nom de la société
        {{user_name}} - Nom de l'utilisateur"""
    )

    # Aperçu du message (calculé)
    preview = fields.Text(
        string='Aperçu',
        compute='_compute_preview'
    )

    @api.depends('body')
    def _compute_preview(self):
        """Génère un aperçu du message avec des valeurs d'exemple"""
        example_values = {
            'partner_name': 'Client Exemple',
            'document_name': 'SO001',
            'document_date': '26/01/2026',
            'amount_total': '150,000.00',
            'currency': 'DZD',
            'company_name': 'Ma Société',
            'user_name': 'Commercial',
        }
        for record in self:
            if record.body:
                preview = record.body
                for key, value in example_values.items():
                    preview = preview.replace('{{%s}}' % key, value)
                record.preview = preview
            else:
                record.preview = ''

    def render_message(self, document):
        """Rend le message avec les valeurs du document"""
        self.ensure_one()

        # Récupérer les valeurs selon le type de document
        values = self._get_document_values(document)

        # Remplacer les placeholders
        message = self.body or ''
        for key, value in values.items():
            message = message.replace('{{%s}}' % key, str(value or ''))

        return message

    def _get_document_values(self, document):
        """Extrait les valeurs d'un document pour le rendu du template"""
        values = {
            'partner_name': '',
            'document_name': document.name or '',
            'document_date': '',
            'amount_total': '',
            'currency': '',
            'company_name': document.company_id.name if document.company_id else '',
            'user_name': self.env.user.name or '',
        }

        # Gestion selon le type de modèle
        model_name = document._name

        if model_name == 'sale.order':
            values['partner_name'] = document.partner_id.name or ''
            values['document_date'] = document.date_order.strftime('%d/%m/%Y') if document.date_order else ''
            values['amount_total'] = '{:,.2f}'.format(document.amount_total)
            values['currency'] = document.currency_id.name or ''

        elif model_name == 'account.move':
            values['partner_name'] = document.partner_id.name or ''
            values['document_date'] = document.invoice_date.strftime('%d/%m/%Y') if document.invoice_date else ''
            values['amount_total'] = '{:,.2f}'.format(document.amount_total)
            values['currency'] = document.currency_id.name or ''

        elif model_name == 'purchase.order':
            values['partner_name'] = document.partner_id.name or ''
            values['document_date'] = document.date_order.strftime('%d/%m/%Y') if document.date_order else ''
            values['amount_total'] = '{:,.2f}'.format(document.amount_total)
            values['currency'] = document.currency_id.name or ''

        return values

    @api.model
    def get_default_templates(self):
        """Retourne les templates par défaut pour chaque type"""
        return {
            'sale_quotation': _(
                "Bonjour {{partner_name}},\n\n"
                "Veuillez trouver ci-joint notre devis {{document_name}} "
                "d'un montant de {{amount_total}} {{currency}}.\n\n"
                "N'hésitez pas à nous contacter pour toute question.\n\n"
                "Cordialement,\n{{user_name}}\n{{company_name}}"
            ),
            'sale_order': _(
                "Bonjour {{partner_name}},\n\n"
                "Veuillez trouver ci-joint votre bon de commande {{document_name}} "
                "d'un montant de {{amount_total}} {{currency}}.\n\n"
                "Cordialement,\n{{user_name}}\n{{company_name}}"
            ),
            'invoice': _(
                "Bonjour {{partner_name}},\n\n"
                "Veuillez trouver ci-joint votre facture {{document_name}} "
                "du {{document_date}} d'un montant de {{amount_total}} {{currency}}.\n\n"
                "Cordialement,\n{{user_name}}\n{{company_name}}"
            ),
            'credit_note': _(
                "Bonjour {{partner_name}},\n\n"
                "Veuillez trouver ci-joint votre avoir {{document_name}} "
                "d'un montant de {{amount_total}} {{currency}}.\n\n"
                "Cordialement,\n{{user_name}}\n{{company_name}}"
            ),
            'purchase_rfq': _(
                "Bonjour {{partner_name}},\n\n"
                "Veuillez trouver ci-joint notre demande de prix {{document_name}}.\n\n"
                "Merci de nous faire parvenir votre meilleure offre.\n\n"
                "Cordialement,\n{{user_name}}\n{{company_name}}"
            ),
            'purchase_order': _(
                "Bonjour {{partner_name}},\n\n"
                "Veuillez trouver ci-joint notre bon de commande {{document_name}} "
                "d'un montant de {{amount_total}} {{currency}}.\n\n"
                "Cordialement,\n{{user_name}}\n{{company_name}}"
            ),
        }
