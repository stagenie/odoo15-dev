# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ReturnOrderLine(models.Model):
    _name = 'return.order.line'
    _description = 'Ligne d\'ordre de retour'
    _order = 'sequence, id'

    return_order_id = fields.Many2one(
        'return.order',
        string='Ordre de retour',
        required=True,
        ondelete='cascade'
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )

    # Produit avec domaine dynamique
    product_id = fields.Many2one(
        'product.product',
        string='Produit',
        required=True,
        domain="[('id', 'in', available_product_ids)]"
    )

    # Produits disponibles (compute)
    available_product_ids = fields.Many2many(
        'product.product',
        compute='_compute_available_product_ids',
        string='Produits disponibles'
    )

    qty_returned = fields.Float(
        string='Quantite retournee',
        required=True,
        default=1.0
    )

    qty_available = fields.Float(
        string='Quantite disponible',
        compute='_compute_qty_available',
        help="Quantite disponible dans l'emplacement de retour"
    )

    # Prix et sous-total
    price_unit = fields.Float(
        string='Prix unitaire',
        compute='_compute_price_unit',
        store=True,
        readonly=False
    )

    subtotal = fields.Monetary(
        string='Sous-total',
        compute='_compute_subtotal',
        store=True,
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        related='return_order_id.currency_id',
        string='Devise'
    )

    # Lien optionnel vers stock.move.line (si origine strict)
    picking_line_id = fields.Many2one(
        'stock.move.line',
        string='Ligne BL d\'origine'
    )

    # Reference du BL pour affichage
    picking_id = fields.Many2one(
        related='picking_line_id.picking_id',
        string='BL origine',
        store=True
    )

    # Champs lies pour le domaine
    partner_id = fields.Many2one(
        related='return_order_id.partner_id',
        string='Client'
    )

    origin_mode = fields.Selection(
        related='return_order_id.origin_mode',
        string='Mode origine'
    )

    order_picking_ids = fields.Many2many(
        related='return_order_id.picking_ids',
        string='BL de l\'ordre'
    )

    @api.depends('return_order_id.origin_mode',
                 'return_order_id.picking_ids',
                 'return_order_id.partner_id')
    def _compute_available_product_ids(self):
        """Calcule les produits disponibles selon le mode d'origine"""
        for line in self:
            origin_mode = line.return_order_id.origin_mode
            partner = line.return_order_id.partner_id

            if origin_mode == 'strict' and line.return_order_id.picking_ids:
                # Mode strict : produits des BL selectionnes uniquement
                move_lines = line.return_order_id.picking_ids.mapped('move_line_ids')
                line.available_product_ids = move_lines.mapped('product_id')

            elif origin_mode == 'flexible' and partner:
                # Mode flexible : tous les produits deja livres au client
                # Rechercher tous les BL sortants termines pour ce client
                delivered_pickings = self.env['stock.picking'].search([
                    ('partner_id', '=', partner.id),
                    ('state', '=', 'done'),
                    ('picking_type_code', '=', 'outgoing')
                ])
                if delivered_pickings:
                    move_lines = delivered_pickings.mapped('move_line_ids')
                    line.available_product_ids = move_lines.mapped('product_id')
                else:
                    # Aucune livraison trouvee, liste vide
                    line.available_product_ids = self.env['product.product']

            else:
                # Mode none : tous les produits stockables
                line.available_product_ids = self.env['product.product'].search([
                    ('type', 'in', ['product', 'consu'])
                ])

    @api.depends('product_id', 'return_order_id.return_location_id')
    def _compute_qty_available(self):
        """Calcule la quantite disponible via stock.quant"""
        for line in self:
            if line.product_id and line.return_order_id.return_location_id:
                quants = self.env['stock.quant'].search([
                    ('product_id', '=', line.product_id.id),
                    ('location_id', '=', line.return_order_id.return_location_id.id)
                ])
                line.qty_available = sum(
                    quants.mapped(lambda q: q.quantity - q.reserved_quantity)
                )
            else:
                line.qty_available = 0.0

    @api.depends('product_id')
    def _compute_price_unit(self):
        """Prix par defaut du produit"""
        for line in self:
            if line.product_id:
                line.price_unit = line.product_id.lst_price
            else:
                line.price_unit = 0.0

    @api.depends('qty_returned', 'price_unit')
    def _compute_subtotal(self):
        """Calcule le sous-total"""
        for line in self:
            line.subtotal = line.qty_returned * line.price_unit

    @api.onchange('picking_line_id')
    def _onchange_picking_line_id(self):
        """Remplit automatiquement les champs depuis la ligne BL"""
        if self.picking_line_id:
            self.product_id = self.picking_line_id.product_id
            self.qty_returned = self.picking_line_id.qty_done
