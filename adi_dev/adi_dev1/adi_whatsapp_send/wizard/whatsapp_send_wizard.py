# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import urllib.parse
import re


class WhatsappSendWizard(models.TransientModel):
    _name = 'whatsapp.send.wizard'
    _description = 'Assistant d\'envoi WhatsApp'

    # Référence au document source
    res_model = fields.Char(string='Modèle', required=True)
    res_id = fields.Integer(string='ID Enregistrement', required=True)

    # Type de document (déterminé automatiquement)
    document_type = fields.Selection([
        ('sale_quotation', 'Devis Client'),
        ('sale_order', 'Bon de Commande Client'),
        ('invoice', 'Facture Client'),
        ('credit_note', 'Avoir Client'),
        ('purchase_rfq', 'Demande de Prix Fournisseur'),
        ('purchase_order', 'Bon de Commande Fournisseur'),
    ], string='Type de Document', readonly=True)

    # Partenaire et téléphone
    partner_id = fields.Many2one(
        'res.partner',
        string='Destinataire',
        required=True
    )
    phone_number = fields.Char(
        string='Numéro WhatsApp',
        required=True,
        help="Numéro de téléphone au format international (ex: +213555123456)"
    )

    # Message
    template_id = fields.Many2one(
        'whatsapp.message.template',
        string='Template',
        domain="[('document_type', 'in', [document_type, 'all'])]"
    )
    message = fields.Text(
        string='Message',
        required=True
    )

    # Informations du document (affichage)
    document_name = fields.Char(string='Document', readonly=True)
    amount_total = fields.Char(string='Montant', readonly=True)

    @api.model
    def default_get(self, fields_list):
        """Initialise le wizard avec les valeurs par défaut"""
        res = super().default_get(fields_list)

        # Récupérer le contexte
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')

        if not active_model or not active_id:
            return res

        res['res_model'] = active_model
        res['res_id'] = active_id

        # Récupérer le document
        document = self.env[active_model].browse(active_id)
        if not document.exists():
            return res

        # Déterminer le type de document
        document_type = self._get_document_type(active_model, document)
        res['document_type'] = document_type

        # Récupérer le partenaire
        partner = document.partner_id if hasattr(document, 'partner_id') else False
        if partner:
            res['partner_id'] = partner.id
            # Récupérer le numéro de téléphone
            phone = self._format_phone_number(partner.mobile or partner.phone or '')
            res['phone_number'] = phone

        # Informations du document
        res['document_name'] = document.name or ''
        if hasattr(document, 'amount_total') and hasattr(document, 'currency_id'):
            res['amount_total'] = '{:,.2f} {}'.format(
                document.amount_total,
                document.currency_id.name or ''
            )

        # Récupérer la configuration
        config = self.env['whatsapp.document.config'].get_config_for_document(
            document_type,
            document.company_id.id if hasattr(document, 'company_id') else False
        )

        if config:
            # Template de message par défaut
            if config.template_id:
                res['template_id'] = config.template_id.id
                res['message'] = config.template_id.render_message(document)
        else:
            # Message par défaut si pas de configuration
            res['message'] = self._get_default_message(document, document_type)

        return res

    def _get_document_type(self, model, document):
        """Détermine le type de document"""
        if model == 'sale.order':
            if document.state in ('draft', 'sent'):
                return 'sale_quotation'
            return 'sale_order'
        elif model == 'account.move':
            if document.move_type == 'out_refund':
                return 'credit_note'
            return 'invoice'
        elif model == 'purchase.order':
            if document.state in ('draft', 'sent'):
                return 'purchase_rfq'
            return 'purchase_order'
        return False

    def _format_phone_number(self, phone):
        """Formate le numéro de téléphone pour WhatsApp"""
        if not phone:
            return ''

        # Supprimer tous les caractères non numériques sauf le +
        phone = re.sub(r'[^\d+]', '', phone)

        # Si commence par 0, ajouter le préfixe Algérie
        if phone.startswith('0'):
            phone = '+213' + phone[1:]
        elif not phone.startswith('+'):
            phone = '+' + phone

        return phone

    def _get_default_message(self, document, document_type):
        """Génère un message par défaut si pas de template"""
        templates = self.env['whatsapp.message.template'].get_default_templates()
        template_body = templates.get(document_type, '')

        if template_body:
            # Créer un template temporaire pour le rendu
            temp_template = self.env['whatsapp.message.template'].new({
                'body': template_body
            })
            return temp_template.render_message(document)

        return "Bonjour,\n\nVeuillez trouver ci-joint le document %s.\n\nCordialement" % document.name

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Met à jour le message quand le template change"""
        if self.template_id and self.res_model and self.res_id:
            document = self.env[self.res_model].browse(self.res_id)
            if document.exists():
                self.message = self.template_id.render_message(document)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Met à jour le numéro de téléphone quand le partenaire change"""
        if self.partner_id:
            self.phone_number = self._format_phone_number(
                self.partner_id.mobile or self.partner_id.phone or ''
            )

    def action_send_whatsapp(self):
        """Ouvre WhatsApp Web avec le message pré-rempli"""
        self.ensure_one()

        # Valider le numéro de téléphone
        if not self.phone_number:
            raise UserError("Veuillez saisir un numéro de téléphone WhatsApp.")

        phone = self._format_phone_number(self.phone_number)
        if not phone or len(phone) < 10:
            raise UserError("Le numéro de téléphone n'est pas valide.")

        # Supprimer le + pour l'URL WhatsApp
        phone_for_url = phone.replace('+', '')

        # Encoder le message pour l'URL
        message_encoded = urllib.parse.quote(self.message or '')

        # Construire l'URL WhatsApp
        whatsapp_url = f"https://wa.me/{phone_for_url}?text={message_encoded}"

        # Enregistrer dans le chatter du document
        document = self.env[self.res_model].browse(self.res_id)
        if document.exists() and hasattr(document, 'message_post'):
            body = (
                "<p><strong>📱 Message WhatsApp envoyé</strong></p>"
                "<p><strong>Destinataire:</strong> {} ({})</p>"
                "<p><strong>Message:</strong></p><pre>{}</pre>"
            ).format(self.partner_id.name, self.phone_number, self.message)

            document.message_post(
                body=body,
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )

        # Retourner l'action pour ouvrir WhatsApp
        return {
            'type': 'ir.actions.act_url',
            'url': whatsapp_url,
            'target': 'new',
        }
