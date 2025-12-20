# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AbPaymentModality(models.Model):
    _name = 'ab.payment.modality'
    _description = 'Modalité de paiement'
    _order = 'sequence, id'

    name = fields.Char(
        string='Nom',
        required=True,
        help='Nom de la modalité de paiement (ex: 50% Commande - 30% Livraison - 20% Réception)'
    )
    sequence = fields.Integer(
        string='Séquence',
        default=10,
        help='Ordre d\'affichage'
    )
    active = fields.Boolean(
        string='Actif',
        default=True
    )
    description = fields.Text(
        string='Description',
        help='Description détaillée de la modalité de paiement'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        default=lambda self: self.env.company
    )

    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)',
         'Le nom de la modalité doit être unique par société!')
    ]
