# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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
        string='Ligne BL d\'origine'
    )

    # Reference du BL pour affichage (mode strict via picking_line_id)
    picking_id = fields.Many2one(
        related='picking_line_id.picking_id',
        string='BL origine',
        store=True
    )

    # BL d'origine pour mode souple (stocke directement car pas de picking_line_id)
    origin_picking_id = fields.Many2one(
        'stock.picking',
        string='BL d\'origine (souple)',
        help="BL d'origine en mode souple (quand picking_line_id n'est pas renseigne)"
    )

    # Lien vers la ligne de commande d'origine (pour tracer le prix)
    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Ligne de commande d\'origine',
        help="Ligne de commande d'origine pour recuperer le prix de vente"
    )

    # Champ compute pour afficher le BL effectif (strict ou souple)
    effective_picking_id = fields.Many2one(
        'stock.picking',
        string='BL effectif',
        compute='_compute_effective_picking_id',
        store=True,
        help="BL d'origine effectif (strict ou souple)"
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

    @api.constrains('product_id')
    def _check_product_in_available_list(self):
        """
        Verifie que le produit selectionne est bien dans la liste des produits autorises.
        Cette contrainte empeche la selection de produits non vendus au client
        meme via la recherche avancee.
        """
        for line in self:
            if not line.product_id or not line.return_order_id:
                continue

            origin_mode = line.return_order_id.origin_mode
            partner = line.return_order_id.partner_id

            # Mode STRICT : verifier que le produit est dans les BL selectionnes
            if origin_mode == 'strict':
                if line.return_order_id.picking_ids:
                    move_lines = line.return_order_id.picking_ids.mapped('move_line_ids')
                    allowed_products = move_lines.mapped('product_id')
                    if line.product_id not in allowed_products:
                        raise ValidationError(_(
                            "Le produit '%s' n'appartient pas aux bons de livraison selectionnes.\n"
                            "En mode strict, seuls les produits des BL d'origine peuvent etre retournes."
                        ) % line.product_id.display_name)

            # Mode SOUPLE : verifier que le produit a ete livre au client
            elif origin_mode == 'flexible' and partner:
                delivered_pickings = self.env['stock.picking'].search([
                    ('partner_id', '=', partner.id),
                    ('state', '=', 'done'),
                    ('picking_type_code', '=', 'outgoing')
                ])
                if delivered_pickings:
                    move_lines = delivered_pickings.mapped('move_line_ids')
                    allowed_products = move_lines.mapped('product_id')
                    if line.product_id not in allowed_products:
                        raise ValidationError(_(
                            "Le produit '%s' n'a jamais ete livre au client '%s'.\n"
                            "En mode souple, seuls les produits deja livres peuvent etre retournes."
                        ) % (line.product_id.display_name, partner.name))
                else:
                    raise ValidationError(_(
                        "Aucune livraison trouvee pour le client '%s'.\n"
                        "En mode souple, le client doit avoir au moins une livraison terminee."
                    ) % partner.name)

    @api.depends('picking_line_id', 'origin_picking_id')
    def _compute_effective_picking_id(self):
        """Calcule le BL effectif (mode strict ou souple)"""
        for line in self:
            if line.picking_line_id:
                # Mode strict: BL via picking_line_id
                line.effective_picking_id = line.picking_line_id.picking_id
            elif line.origin_picking_id:
                # Mode souple: BL stocke directement
                line.effective_picking_id = line.origin_picking_id
            else:
                line.effective_picking_id = False

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

    @api.depends('product_id', 'picking_line_id', 'origin_picking_id', 'sale_line_id')
    def _compute_price_unit(self):
        """
        Recupere le prix de vente original et la remise depuis la commande client.

        Logique:
        - Mode STRICT: picking_line_id → picking_id → sale_id → sale.order.line
        - Mode SOUPLE: origin_picking_id → sale_id → sale.order.line
                       ou recherche dans les BL livres du client
        - Mode LIBRE: prix catalogue (lst_price)
        """
        for line in self:
            if not line.product_id:
                line.price_unit = 0.0
                line.discount = 0.0
                continue

            # Essayer de recuperer le prix depuis sale_line_id si deja renseigne
            if line.sale_line_id:
                line.price_unit = line.sale_line_id.price_unit
                line.discount = line.sale_line_id.discount
                continue

            # Tenter de trouver le prix original
            price, discount = line._get_original_sale_price()
            if price:
                line.price_unit = price
                line.discount = discount
            else:
                line.price_unit = line.product_id.lst_price
                line.discount = 0.0

    def _get_original_sale_price(self):
        """
        Recherche le prix de vente original et la remise depuis la commande client.

        Retourne un tuple (price, discount) ou (False, 0.0) si non trouve.
        Met a jour sale_line_id si une ligne de commande est trouvee.
        """
        self.ensure_one()

        if not self.product_id:
            return False, 0.0

        sale_line = False
        origin_mode = self.return_order_id.origin_mode

        # =============================================
        # Mode STRICT: via picking_line_id
        # =============================================
        if origin_mode == 'strict' and self.picking_line_id:
            picking = self.picking_line_id.picking_id
            if picking and picking.sale_id:
                # Chercher la ligne de commande correspondante
                sale_line = picking.sale_id.order_line.filtered(
                    lambda l: l.product_id == self.product_id
                )
                if sale_line:
                    sale_line = sale_line[0]  # Prendre la premiere si plusieurs

        # =============================================
        # Mode SOUPLE: via origin_picking_id ou recherche
        # =============================================
        elif origin_mode == 'flexible':
            # D'abord verifier si on a un origin_picking_id
            if self.origin_picking_id and self.origin_picking_id.sale_id:
                sale_line = self.origin_picking_id.sale_id.order_line.filtered(
                    lambda l: l.product_id == self.product_id
                )
                if sale_line:
                    sale_line = sale_line[0]

            # Sinon rechercher dans tous les BL livres au client
            if not sale_line and self.partner_id:
                # Rechercher les BL sortants termines pour ce client/produit
                pickings = self.env['stock.picking'].search([
                    ('partner_id', '=', self.partner_id.id),
                    ('state', '=', 'done'),
                    ('picking_type_code', '=', 'outgoing'),
                    ('sale_id', '!=', False),
                ], order='date_done desc')

                for picking in pickings:
                    # Verifier si ce BL contient le produit
                    if self.product_id in picking.move_line_ids.mapped('product_id'):
                        # Chercher la ligne de commande
                        sale_line = picking.sale_id.order_line.filtered(
                            lambda l: l.product_id == self.product_id
                        )
                        if sale_line:
                            sale_line = sale_line[0]
                            # Stocker le BL d'origine pour reference future
                            if not self.origin_picking_id:
                                self.origin_picking_id = picking
                            break

        # =============================================
        # Mode LIBRE: pas de recherche, prix catalogue
        # =============================================
        # (on ne fait rien, retourne False)

        # Si on a trouve une ligne de commande, mettre a jour sale_line_id
        if sale_line:
            self.sale_line_id = sale_line
            return sale_line.price_unit, sale_line.discount

        return False, 0.0

    @api.depends('qty_returned', 'price_unit', 'discount')
    def _compute_subtotal(self):
        """Calcule le sous-total en tenant compte de la remise"""
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            line.subtotal = line.qty_returned * price

    @api.onchange('picking_line_id')
    def _onchange_picking_line_id(self):
        """Remplit automatiquement les champs depuis la ligne BL"""
        if self.picking_line_id:
            self.product_id = self.picking_line_id.product_id
            self.qty_returned = self.picking_line_id.qty_done

            # Recuperer la ligne de commande d'origine pour le prix et la remise
            picking = self.picking_line_id.picking_id
            if picking and picking.sale_id:
                sale_line = picking.sale_id.order_line.filtered(
                    lambda l: l.product_id == self.product_id
                )
                if sale_line:
                    self.sale_line_id = sale_line[0]
                    self.price_unit = sale_line[0].price_unit
                    self.discount = sale_line[0].discount

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """
        Quand le produit change, recherche le prix de vente original.
        Utile en mode souple ou libre.
        """
        if not self.product_id:
            self.sale_line_id = False
            self.origin_picking_id = False
            return

        # En mode strict avec picking_line_id, le prix est deja gere
        if self.origin_mode == 'strict' and self.picking_line_id:
            return

        # En mode souple, rechercher le prix de vente original
        if self.origin_mode == 'flexible' and self.partner_id:
            # Rechercher le dernier BL livre contenant ce produit
            pickings = self.env['stock.picking'].search([
                ('partner_id', '=', self.partner_id.id),
                ('state', '=', 'done'),
                ('picking_type_code', '=', 'outgoing'),
                ('sale_id', '!=', False),
            ], order='date_done desc')

            for picking in pickings:
                if self.product_id in picking.move_line_ids.mapped('product_id'):
                    # Trouver la ligne de commande
                    sale_line = picking.sale_id.order_line.filtered(
                        lambda l: l.product_id == self.product_id
                    )
                    if sale_line:
                        self.origin_picking_id = picking
                        self.sale_line_id = sale_line[0]
                        self.price_unit = sale_line[0].price_unit
                        self.discount = sale_line[0].discount
                        break
