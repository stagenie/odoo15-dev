# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Champs pour le bon de commande
    delivery_deadline = fields.Date(
        string='Délais de livraison',
        help='Date limite de livraison pour ce bon de commande'
    )
    payment_terms_custom = fields.Text(
        string='Modalités de paiement',
        help='Modalités de paiement personnalisées (ex: 50% 30% 20%)',
        default='50% à la commande, 30% à la livraison, 20% à la réception'
    )

    # Champ pour la validité de l'offre (devis/proforma)
    quotation_validity_date = fields.Date(
        string='Offre valable jusqu\'au',
        help='Date de validité de l\'offre',
        compute='_compute_quotation_validity_date',
        store=True,
        readonly=False
    )

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
