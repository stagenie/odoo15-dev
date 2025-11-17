# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CashExpenseLine(models.Model):
    _name = 'cash.expense.line'
    _description = 'Ligne de dépense de caisse'
    _order = 'expense_id, sequence, id'

    sequence = fields.Integer(
        string='Séquence',
        default=10
    )

    expense_id = fields.Many2one(
        'cash.expense',
        string='Dépense',
        required=True,
        ondelete='cascade'
    )

    name = fields.Char(
        string='Description',
        required=True
    )

    product_id = fields.Many2one(
        'product.product',
        string='Article',
        help="Article optionnel pour suivre les achats"
    )

    quantity = fields.Float(
        string='Quantité',
        default=1.0,
        digits='Product Unit of Measure'
    )

    unit_price = fields.Monetary(
        string='Prix unitaire',
        required=True,
        currency_field='currency_id'
    )

    total_amount = fields.Monetary(
        string='Montant total',
        compute='_compute_total_amount',
        store=True,
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='expense_id.currency_id',
        store=True
    )

    notes = fields.Text(
        string='Notes'
    )

    # Pièces jointes spécifiques à cette ligne
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'cash_expense_line_attachment_rel',
        'line_id',
        'attachment_id',
        string='Justificatifs',
        help="Factures, reçus pour cette ligne spécifique"
    )

    attachment_count = fields.Integer(
        compute='_compute_attachment_count',
        string='Nombre de pièces jointes'
    )

    company_id = fields.Many2one(
        'res.company',
        related='expense_id.company_id',
        store=True
    )

    @api.depends('quantity', 'unit_price')
    def _compute_total_amount(self):
        """Calculer le montant total de la ligne"""
        for line in self:
            line.total_amount = line.quantity * line.unit_price

    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        """Compter les pièces jointes"""
        for line in self:
            line.attachment_count = len(line.attachment_ids)

    @api.constrains('quantity', 'unit_price')
    def _check_amounts(self):
        """Vérifier que les montants sont positifs"""
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_("La quantité doit être positive !"))
            if line.unit_price < 0:
                raise ValidationError(_("Le prix unitaire ne peut pas être négatif !"))

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Remplir automatiquement le nom et le prix depuis l'article"""
        if self.product_id:
            self.name = self.product_id.name
            self.unit_price = self.product_id.list_price

    def name_get(self):
        """Affichage personnalisé"""
        result = []
        for line in self:
            name = f"{line.name} - {line.total_amount} {line.currency_id.symbol}"
            result.append((line.id, name))
        return result
