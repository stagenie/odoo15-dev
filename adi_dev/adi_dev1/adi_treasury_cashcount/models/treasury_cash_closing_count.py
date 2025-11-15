# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TreasuryCashClosingCount(models.Model):
    _name = 'treasury.cash.closing.count'
    _description = 'Ligne de Comptage de Clôture'
    _order = 'denomination_id'

    closing_id = fields.Many2one(
        'treasury.cash.closing',
        string='Clôture',
        required=True,
        ondelete='cascade',
        index=True
    )

    denomination_id = fields.Many2one(
        'cash.denomination',
        string='Dénomination',
        required=True,
        ondelete='restrict',
        domain="[('currency_id', '=', currency_id)]"
    )

    quantity = fields.Integer(
        string='Nombre',
        default=0,
        help="Nombre de billets ou pièces comptés"
    )

    subtotal = fields.Monetary(
        string='Sous-total',
        currency_field='currency_id',
        compute='_compute_subtotal',
        store=True,
        help="Quantité × Valeur de la dénomination"
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='closing_id.currency_id',
        store=True,
        readonly=True
    )

    denomination_value = fields.Monetary(
        string='Valeur unitaire',
        related='denomination_id.value',
        currency_field='currency_id',
        readonly=True
    )

    denomination_type = fields.Selection(
        related='denomination_id.type',
        string='Type',
        readonly=True
    )

    @api.depends('quantity', 'denomination_id.value')
    def _compute_subtotal(self):
        """Calculer le sous-total = quantité × valeur"""
        for line in self:
            if line.denomination_id and line.quantity:
                line.subtotal = line.quantity * line.denomination_id.value
            else:
                line.subtotal = 0.0

    @api.constrains('quantity')
    def _check_quantity_positive(self):
        """Vérifier que la quantité n'est pas négative"""
        for line in self:
            if line.quantity < 0:
                raise ValidationError(
                    _("La quantité ne peut pas être négative !")
                )

    @api.onchange('denomination_id')
    def _onchange_denomination_id(self):
        """Initialiser la quantité à 0 lors du changement de dénomination"""
        if self.denomination_id and not self.quantity:
            self.quantity = 0
