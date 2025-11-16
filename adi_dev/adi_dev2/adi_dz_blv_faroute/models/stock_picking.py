# -*- coding: utf-8 -*-

from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    num_fact = fields.Char("N° de Facture de R")

    sale_order_amount = fields.Float(string="Sale Order Amount",
                                     compute="_compute_sale_order_amount", store=True)

    """ 
    @api.depends('move_lines', 'sale_id')
    def _compute_sale_order_amount(self):
        for picking in self:
            total_amount = 0.0
            # Loop through the stock.move lines of the picking
            for move in picking.move_lines:
                # Get the sale order line associated with the product in the stock.move
                sale_order_line = move.sale_line_id
                if sale_order_line:
                    # Calculate the amount based on the sale order line
                    total_amount += sale_order_line.price_total
            picking.sale_order_amount = total_amount

    """
    


    @api.depends('move_ids_without_package.sale_line_id', 'move_ids_without_package.quantity_done', 'sale_id')
    def _compute_sale_order_amount(self):
        for picking in self:
            total_amount_ht = 0.0
            for move in picking.move_ids_without_package:
                sale_line = move.sale_line_id
                if sale_line:
                    # Utiliser la quantité livrée
                    quantity = move.quantity_done
                    # Prix unitaire HT
                    price_unit_ht = sale_line.price_unit
                    # Remise éventuelle
                    discount = sale_line.discount / 100.0 if sale_line.discount else 0.0
                    
                    # Calcul du montant HT pour cette ligne
                    line_amount_ht = quantity * price_unit_ht * (1 - discount)
                    
                    # Ajouter au total HT
                    total_amount_ht += line_amount_ht
            picking.sale_order_amount = total_amount_ht

    # Champ calculé pour la TVA (19 % du Montant HT)
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.user.company_id.currency_id
    )

    tva_amount = fields.Monetary(
        string="TVA (19%)",
        compute='_compute_ttc',
        store=True,
        currency_field='currency_id'
    )

    # Champ calculé pour le total HT + TVA
    total_ttc = fields.Monetary(
        string="Total TTC ",
        compute='_compute_ttc',
        store=True,
        currency_field='currency_id'
    )

    @api.depends('sale_order_amount')
    def _compute_ttc(self):
        for order in self:
            # Calcul de la TVA : 19% du Montant HT
            order.tva_amount = order.sale_order_amount * 0.19
            # Calcul du Total avec TVA : Montant HT + TVA
            order.total_ttc = order.sale_order_amount + order.tva_amount

    def get_amount_to_text_ttcdz(self):
        return self.currency_id.amount_to_text_dz(self.total_ttc)


