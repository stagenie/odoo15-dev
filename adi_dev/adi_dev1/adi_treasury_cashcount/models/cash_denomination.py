# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CashDenomination(models.Model):
    _name = 'cash.denomination'
    _description = 'Dénomination de Billets et Pièces'
    _order = 'value desc'

    name = fields.Char(
        string='Nom',
        required=True,
        help="Nom de la dénomination (ex: Billet de 2000 DA)"
    )

    value = fields.Monetary(
        string='Valeur',
        required=True,
        currency_field='currency_id',
        help="Valeur faciale du billet ou de la pièce"
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    type = fields.Selection([
        ('bill', 'Billet'),
        ('coin', 'Pièce')
    ], string='Type', required=True, default='bill')

    active = fields.Boolean(
        string='Actif',
        default=True,
        help="Décocher pour archiver une dénomination obsolète"
    )

    sequence = fields.Integer(
        string='Séquence',
        default=10,
        help="Ordre d'affichage dans le comptage"
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        default=lambda self: self.env.company
    )

    @api.constrains('value')
    def _check_value_positive(self):
        """Vérifier que la valeur est positive"""
        for denomination in self:
            if denomination.value <= 0:
                raise ValidationError(
                    _("La valeur d'une dénomination doit être strictement positive !")
                )

    def name_get(self):
        """Affichage personnalisé"""
        result = []
        for denomination in self:
            type_icon = '💵' if denomination.type == 'bill' else '🪙'
            name = f"{type_icon} {denomination.name}"
            result.append((denomination.id, name))
        return result
