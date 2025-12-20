# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Champs pour le bon de commande
    delivery_deadline = fields.Date(
        string='Délai de livraison',
        help='Date de livraison prévue pour ce bon de commande'
    )

    payment_modality_id = fields.Many2one(
        'ab.payment.modality',
        string='Modalité de paiement',
        help='Sélectionnez une modalité de paiement prédéfinie'
    )

    payment_modality_text = fields.Char(
        string='Modalité de paiement (texte)',
        compute='_compute_payment_modality_text',
        store=True,
        readonly=False,
        help='Texte de la modalité de paiement (modifiable)'
    )

    # Champ pour la validité de l'offre (devis/proforma)
    quotation_validity_date = fields.Date(
        string='Offre valable jusqu\'au',
        help='Date de validité de l\'offre',
        compute='_compute_quotation_validity_date',
        store=True,
        readonly=False
    )

    @api.depends('payment_modality_id')
    def _compute_payment_modality_text(self):
        """Récupère le texte de la modalité sélectionnée"""
        for order in self:
            if order.payment_modality_id:
                order.payment_modality_text = order.payment_modality_id.name
            elif not order.payment_modality_text:
                order.payment_modality_text = False

    @api.depends('validity_date', 'date_order')
    def _compute_quotation_validity_date(self):
        """Calcule la date de validité par défaut si validity_date existe"""
        for order in self:
            if hasattr(order, 'validity_date') and order.validity_date:
                order.quotation_validity_date = order.validity_date
            elif order.date_order:
                # Par défaut, 30 jours après la date de commande
                order.quotation_validity_date = fields.Date.add(order.date_order, days=30)
            else:
                order.quotation_validity_date = False

    @api.onchange('payment_modality_id')
    def _onchange_payment_modality_id(self):
        """Met à jour le texte quand on change la modalité"""
        if self.payment_modality_id:
            self.payment_modality_text = self.payment_modality_id.name
