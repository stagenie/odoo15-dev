# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockPrintWizard(models.TransientModel):
    _name = 'stock.print.wizard'
    _description = 'Assistant d\'impression du stock'

    print_type = fields.Selection([
        ('all_products', 'Tous les produits'),
        ('all_stock', 'Tout le stock (quantité >= 0)'),
        ('current_stock', 'Stock actuel uniquement (quantité > 0)'),
    ], string='Type d\'impression', default='current_stock', required=True)

    category_ids = fields.Many2many(
        'product.category',
        'stock_print_wizard_category_rel',
        'wizard_id',
        'category_id',
        string='Catégories',
        help='Laissez vide pour inclure toutes les catégories'
    )

    include_all_categories = fields.Boolean(
        string='Toutes les catégories',
        default=True,
        help='Cochez pour inclure tous les produits de toutes les catégories'
    )

    @api.onchange('include_all_categories')
    def _onchange_include_all_categories(self):
        if self.include_all_categories:
            self.category_ids = [(5, 0, 0)]

    def _get_products(self):
        """Récupère les produits selon les critères sélectionnés"""
        domain = [('type', '=', 'product')]  # Uniquement les produits stockables

        # Filtre par catégories
        if not self.include_all_categories and self.category_ids:
            # Inclure les catégories enfants
            category_ids = self.category_ids.ids
            all_categories = self.env['product.category'].search([
                ('id', 'child_of', category_ids)
            ])
            domain.append(('categ_id', 'in', all_categories.ids))

        products = self.env['product.product'].search(domain, order='default_code, name')

        # Filtre selon le type d'impression
        if self.print_type == 'all_products':
            return products
        elif self.print_type == 'all_stock':
            return products.filtered(lambda p: p.qty_available >= 0)
        else:  # current_stock
            return products.filtered(lambda p: p.qty_available > 0)

    def _prepare_report_data(self):
        """Prépare les données pour le rapport"""
        products = self._get_products()

        data = []
        total_value_cost = 0
        total_value_sale = 0

        for product in products:
            qty = product.qty_available
            cost = product.standard_price
            sale_price = product.lst_price

            line_data = {
                'reference': product.default_code or '',
                'name': product.name,
                'cost': cost,
                'sale_price': sale_price,
                'qty_available': qty,
                'uom': product.uom_id.name,
                'value_cost': qty * cost,
                'value_sale': qty * sale_price,
            }
            data.append(line_data)
            total_value_cost += line_data['value_cost']
            total_value_sale += line_data['value_sale']

        return {
            'products': data,
            'total_value_cost': total_value_cost,
            'total_value_sale': total_value_sale,
            'print_type': dict(self._fields['print_type'].selection).get(self.print_type),
            'categories': ', '.join(self.category_ids.mapped('complete_name')) if not self.include_all_categories and self.category_ids else 'Toutes les catégories',
            'company': self.env.company,
            'date': fields.Date.today(),
            'total_products': len(data),
            'total_qty': sum(p['qty_available'] for p in data),
        }

    def action_print(self):
        """Génère le rapport PDF"""
        self.ensure_one()
        return self.env.ref('adi_stock_print.action_report_stock_print').report_action(self)
