# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SupplierReturnOrderLine(models.Model):
    _name = 'supplier.return.order.line'
    _description = 'Ligne d\'ordre de retour fournisseur'
    _order = 'sequence, id'

    return_order_id = fields.Many2one(
        'supplier.return.order',
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
        help="Quantite disponible dans l'emplacement source"
    )

    # Prix et sous-total
    price_unit = fields.Float(
        string='Prix unitaire',
        compute='_compute_price_unit',
        store=True,
        readonly=False
    )

    discount = fields.Float(
        string='Remise (%)',
        digits='Discount',
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
        string='Ligne BR d\'origine'
    )

    # Reference du BR pour affichage (mode strict via picking_line_id)
    picking_id = fields.Many2one(
        related='picking_line_id.picking_id',
        string='BR origine',
        store=True
    )

    # BR d'origine pour mode souple (stocke directement car pas de picking_line_id)
    origin_picking_id = fields.Many2one(
        'stock.picking',
        string='BR d\'origine (souple)',
        help="BR d'origine en mode souple (quand picking_line_id n'est pas renseigne)"
    )

    # Lien vers la ligne de commande d'origine (pour tracer le prix)
    purchase_line_id = fields.Many2one(
        'purchase.order.line',
        string='Ligne de commande d\'origine',
        help="Ligne de commande d'origine pour recuperer le prix d'achat"
    )

    # Champ compute pour afficher le BR effectif (strict ou souple)
    effective_picking_id = fields.Many2one(
        'stock.picking',
        string='BR effectif',
        compute='_compute_effective_picking_id',
        store=True,
        help="BR d'origine effectif (strict ou souple)"
    )

    # Champs lies pour le domaine
    partner_id = fields.Many2one(
        related='return_order_id.partner_id',
        string='Fournisseur'
    )

    origin_mode = fields.Selection(
        related='return_order_id.origin_mode',
        string='Mode origine'
    )

    order_picking_ids = fields.Many2many(
        related='return_order_id.picking_ids',
        string='BR de l\'ordre'
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
                # Mode strict : produits des BR selectionnes uniquement
                move_lines = line.return_order_id.picking_ids.mapped('move_line_ids')
                line.available_product_ids = move_lines.mapped('product_id')

            elif origin_mode == 'flexible' and partner:
                # Mode flexible : tous les produits deja recus du fournisseur
                received_pickings = self.env['stock.picking'].search([
                    ('partner_id', '=', partner.id),
                    ('state', '=', 'done'),
                    ('picking_type_code', '=', 'incoming')
                ])
                if received_pickings:
                    move_lines = received_pickings.mapped('move_line_ids')
                    line.available_product_ids = move_lines.mapped('product_id')
                else:
                    line.available_product_ids = self.env['product.product']

            else:
                # Mode none : tous les produits stockables
                line.available_product_ids = self.env['product.product'].search([
                    ('type', 'in', ['product', 'consu'])
                ])

    @api.constrains('product_id')
    def _check_product_in_available_list(self):
        """
        Verifie que le produit selectionne est bien dans la liste des produits autorises.
        Cette contrainte empeche la selection de produits non achetes du fournisseur
        meme via la recherche avancee.
        """
        for line in self:
            if not line.product_id or not line.return_order_id:
                continue

            origin_mode = line.return_order_id.origin_mode
            partner = line.return_order_id.partner_id

            # Mode STRICT : verifier que le produit est dans les BR selectionnes
            if origin_mode == 'strict':
                if line.return_order_id.picking_ids:
                    move_lines = line.return_order_id.picking_ids.mapped('move_line_ids')
                    allowed_products = move_lines.mapped('product_id')
                    if line.product_id not in allowed_products:
                        raise ValidationError(_(
                            "Le produit '%s' n'appartient pas aux bons de reception selectionnes.\n"
                            "En mode strict, seuls les produits des BR d'origine peuvent etre retournes."
                        ) % line.product_id.display_name)

            # Mode SOUPLE : verifier que le produit a ete recu du fournisseur
            elif origin_mode == 'flexible' and partner:
                received_pickings = self.env['stock.picking'].search([
                    ('partner_id', '=', partner.id),
                    ('state', '=', 'done'),
                    ('picking_type_code', '=', 'incoming')
                ])
                if received_pickings:
                    move_lines = received_pickings.mapped('move_line_ids')
                    allowed_products = move_lines.mapped('product_id')
                    if line.product_id not in allowed_products:
                        raise ValidationError(_(
                            "Le produit '%s' n'a jamais ete recu du fournisseur '%s'.\n"
                            "En mode souple, seuls les produits deja recus peuvent etre retournes."
                        ) % (line.product_id.display_name, partner.name))
                else:
                    raise ValidationError(_(
                        "Aucune reception trouvee pour le fournisseur '%s'.\n"
                        "En mode souple, le fournisseur doit avoir au moins une reception terminee."
                    ) % partner.name)

    @api.depends('picking_line_id', 'origin_picking_id')
    def _compute_effective_picking_id(self):
        """Calcule le BR effectif (mode strict ou souple)"""
        for line in self:
            if line.picking_line_id:
                line.effective_picking_id = line.picking_line_id.picking_id
            elif line.origin_picking_id:
                line.effective_picking_id = line.origin_picking_id
            else:
                line.effective_picking_id = False

    @api.depends('product_id', 'return_order_id.source_location_id')
    def _compute_qty_available(self):
        """Calcule la quantite disponible via stock.quant"""
        for line in self:
            if line.product_id and line.return_order_id.source_location_id:
                quants = self.env['stock.quant'].search([
                    ('product_id', '=', line.product_id.id),
                    ('location_id', '=', line.return_order_id.source_location_id.id)
                ])
                line.qty_available = sum(
                    quants.mapped(lambda q: q.quantity - q.reserved_quantity)
                )
            else:
                line.qty_available = 0.0

    @api.depends('product_id', 'picking_line_id', 'origin_picking_id', 'purchase_line_id')
    def _compute_price_unit(self):
        """
        Recupere le prix d'achat original et la remise depuis la commande fournisseur.

        Logique:
        - Mode STRICT: picking_line_id → picking_id → purchase_id → purchase.order.line
        - Mode SOUPLE: origin_picking_id → purchase_id → purchase.order.line
                       ou recherche dans les BR recus du fournisseur
        - Mode LIBRE: prix d'achat standard (standard_price)
        """
        for line in self:
            if not line.product_id:
                line.price_unit = 0.0
                line.discount = 0.0
                continue

            # Essayer de recuperer le prix depuis purchase_line_id si deja renseigne
            if line.purchase_line_id:
                line.price_unit = line.purchase_line_id.price_unit
                line.discount = getattr(line.purchase_line_id, 'discount', 0.0) or 0.0
                continue

            # Tenter de trouver le prix original
            price, discount = line._get_original_purchase_price()
            if price:
                line.price_unit = price
                line.discount = discount
            else:
                line.price_unit = line.product_id.standard_price
                line.discount = 0.0

    def _get_original_purchase_price(self):
        """
        Recherche le prix d'achat original et la remise depuis la commande fournisseur.

        Retourne un tuple (price, discount) ou (False, 0.0) si non trouve.
        Met a jour purchase_line_id si une ligne de commande est trouvee.
        """
        self.ensure_one()

        if not self.product_id:
            return False, 0.0

        purchase_line = False
        origin_mode = self.return_order_id.origin_mode

        # Mode STRICT: via picking_line_id
        if origin_mode == 'strict' and self.picking_line_id:
            picking = self.picking_line_id.picking_id
            if picking and picking.purchase_id:
                purchase_line = picking.purchase_id.order_line.filtered(
                    lambda l: l.product_id == self.product_id
                )
                if purchase_line:
                    purchase_line = purchase_line[0]

        # Mode SOUPLE: via origin_picking_id ou recherche
        elif origin_mode == 'flexible':
            if self.origin_picking_id and self.origin_picking_id.purchase_id:
                purchase_line = self.origin_picking_id.purchase_id.order_line.filtered(
                    lambda l: l.product_id == self.product_id
                )
                if purchase_line:
                    purchase_line = purchase_line[0]

            # Sinon rechercher dans tous les BR recus du fournisseur
            if not purchase_line and self.partner_id:
                pickings = self.env['stock.picking'].search([
                    ('partner_id', '=', self.partner_id.id),
                    ('state', '=', 'done'),
                    ('picking_type_code', '=', 'incoming'),
                    ('purchase_id', '!=', False),
                ], order='date_done desc')

                for picking in pickings:
                    if self.product_id in picking.move_line_ids.mapped('product_id'):
                        purchase_line = picking.purchase_id.order_line.filtered(
                            lambda l: l.product_id == self.product_id
                        )
                        if purchase_line:
                            purchase_line = purchase_line[0]
                            if not self.origin_picking_id:
                                self.origin_picking_id = picking
                            break

        # Si on a trouve une ligne de commande, mettre a jour purchase_line_id
        if purchase_line:
            self.purchase_line_id = purchase_line
            discount = getattr(purchase_line, 'discount', 0.0) or 0.0
            return purchase_line.price_unit, discount

        return False, 0.0

    @api.depends('qty_returned', 'price_unit', 'discount')
    def _compute_subtotal(self):
        """Calcule le sous-total en tenant compte de la remise"""
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            line.subtotal = line.qty_returned * price

    @api.onchange('picking_line_id')
    def _onchange_picking_line_id(self):
        """Remplit automatiquement les champs depuis la ligne BR"""
        if self.picking_line_id:
            self.product_id = self.picking_line_id.product_id
            self.qty_returned = self.picking_line_id.qty_done

            # Recuperer la ligne de commande d'origine pour le prix et la remise
            picking = self.picking_line_id.picking_id
            if picking and picking.purchase_id:
                purchase_line = picking.purchase_id.order_line.filtered(
                    lambda l: l.product_id == self.product_id
                )
                if purchase_line:
                    self.purchase_line_id = purchase_line[0]
                    self.price_unit = purchase_line[0].price_unit
                    self.discount = getattr(purchase_line[0], 'discount', 0.0) or 0.0

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """
        Quand le produit change, recherche le prix d'achat original.
        Utile en mode souple ou libre.
        """
        if not self.product_id:
            self.purchase_line_id = False
            self.origin_picking_id = False
            return

        # En mode strict avec picking_line_id, le prix est deja gere
        if self.origin_mode == 'strict' and self.picking_line_id:
            return

        # En mode souple, rechercher le prix d'achat original
        if self.origin_mode == 'flexible' and self.partner_id:
            pickings = self.env['stock.picking'].search([
                ('partner_id', '=', self.partner_id.id),
                ('state', '=', 'done'),
                ('picking_type_code', '=', 'incoming'),
                ('purchase_id', '!=', False),
            ], order='date_done desc')

            for picking in pickings:
                if self.product_id in picking.move_line_ids.mapped('product_id'):
                    purchase_line = picking.purchase_id.order_line.filtered(
                        lambda l: l.product_id == self.product_id
                    )
                    if purchase_line:
                        self.origin_picking_id = picking
                        self.purchase_line_id = purchase_line[0]
                        self.price_unit = purchase_line[0].price_unit
                        self.discount = getattr(purchase_line[0], 'discount', 0.0) or 0.0
                        break
