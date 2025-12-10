# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StockTransferLine(models.Model):
    _name = 'adi.stock.transfer.line'
    _description = 'Ligne de Transfert de Stock'
    
    transfer_id = fields.Many2one(
        'adi.stock.transfer',
        'Transfert',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    product_id = fields.Many2one(
        'product.product',
        'Produit',
        required=True,
        domain="[('type', 'in', ['product', 'consu'])]"
    )
    
    product_uom_id = fields.Many2one(
        'uom.uom',
        'Unité de Mesure',
        required=True
    )
    
    quantity = fields.Float(
        'Quantité Demandée',
        required=True,
        digits='Product Unit of Measure',
        default=1.0
    )

    qty_sent = fields.Float(
        'Quantité Envoyée',
        digits='Product Unit of Measure',
        default=0.0,
        help="Quantité réellement envoyée par l'entrepôt source"
    )

    qty_received = fields.Float(
        'Quantité Reçue',
        digits='Product Unit of Measure',
        default=0.0,
        help="Quantité réellement reçue par l'entrepôt destination"
    )

    qty_remaining = fields.Float(
        'Reliquat',
        compute='_compute_qty_remaining',
        digits='Product Unit of Measure',
        store=True,
        help="Quantité restante à recevoir (Demandée - Reçue)"
    )

    available_quantity = fields.Float(
        'Quantité Disponible',
        compute='_compute_available_quantity',
        digits='Product Unit of Measure',
        store=False
    )

    line_state = fields.Selection([
        ('pending', 'En attente'),
        ('sent', 'Envoyé'),
        ('partial', 'Partiel'),
        ('done', 'Complet'),
    ], string='État Ligne', default='pending', compute='_compute_line_state', store=True)

    note = fields.Text('Notes')

    # Champ related pour accéder à l'état du transfert parent dans les attrs de la vue
    parent_state = fields.Selection(
        related='transfer_id.state',
        string='État Transfert',
        store=False,
        readonly=True
    )

    # Champs pour contrôler l'édition
    can_edit_qty_sent = fields.Boolean(
        compute='_compute_edit_permissions',
        string='Peut éditer Qté Envoyée'
    )
    can_edit_qty_received = fields.Boolean(
        compute='_compute_edit_permissions',
        string='Peut éditer Qté Reçue'
    )

    @api.depends('transfer_id', 'transfer_id.state')
    def _compute_edit_permissions(self):
        """Calcul des permissions d'édition selon l'état du transfert"""
        for line in self:
            state = line.transfer_id.state if line.transfer_id else False
            # qty_sent éditable seulement en état 'approved'
            line.can_edit_qty_sent = bool(state == 'approved')
            # qty_received éditable seulement en état 'in_transit'
            line.can_edit_qty_received = bool(state == 'in_transit')

    @api.depends('quantity', 'qty_received')
    def _compute_qty_remaining(self):
        """Calcul du reliquat"""
        for line in self:
            line.qty_remaining = line.quantity - line.qty_received

    @api.depends('quantity', 'qty_sent', 'qty_received')
    def _compute_line_state(self):
        """Calcul de l'état de la ligne"""
        for line in self:
            if line.qty_received >= line.quantity:
                line.line_state = 'done'
            elif line.qty_received > 0:
                line.line_state = 'partial'
            elif line.qty_sent > 0:
                line.line_state = 'sent'
            else:
                line.line_state = 'pending'

    @api.depends('product_id', 'transfer_id.source_location_id')
    def _compute_available_quantity(self):
        """Calcul de la quantité disponible dans l'emplacement source"""
        for line in self:
            if line.product_id and line.transfer_id.source_location_id:
                # Utiliser la méthode standard d'Odoo pour obtenir la quantité disponible
                quants = self.env['stock.quant']._gather(
                    line.product_id,
                    line.transfer_id.source_location_id,
                    strict=True
                )
                line.available_quantity = sum(quants.mapped('quantity'))
            else:
                line.available_quantity = 0.0
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Mise à jour de l'unité de mesure lors du changement de produit"""
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id
    
    @api.constrains('quantity')
    def _check_quantity(self):
        """Vérification que la quantité demandée est positive"""
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_(
                    "La quantité demandée doit être strictement positive pour '%s'!"
                ) % line.product_id.display_name)

    @api.constrains('qty_sent')
    def _check_qty_sent(self):
        """Vérification que la quantité envoyée est valide"""
        for line in self:
            if line.qty_sent < 0:
                raise ValidationError(_(
                    "La quantité envoyée ne peut pas être négative pour '%s'!"
                ) % line.product_id.display_name)
            if line.qty_sent > line.quantity:
                raise ValidationError(_(
                    "La quantité envoyée (%.2f) ne peut pas dépasser la quantité demandée (%.2f) pour '%s'!"
                ) % (line.qty_sent, line.quantity, line.product_id.display_name))

    @api.constrains('qty_received')
    def _check_qty_received(self):
        """Vérification que la quantité reçue est valide"""
        for line in self:
            if line.qty_received < 0:
                raise ValidationError(_(
                    "La quantité reçue ne peut pas être négative pour '%s'!"
                ) % line.product_id.display_name)
            # Note: On autorise qty_received > qty_sent pour gérer les cas de surplus
            # (erreur de comptage initial, bonus fournisseur, etc.)
            # Le système affichera un avertissement mais acceptera la saisie
    
    def _check_available_quantity(self):
        """Vérification de la disponibilité du stock"""
        self.ensure_one()
        if self.quantity > self.available_quantity:
            raise ValidationError(_(
                "Quantité insuffisante pour le produit %(product)s!\n"
                "Quantité demandée: %(requested)s\n"
                "Quantité disponible: %(available)s"
            ) % {
                'product': self.product_id.name,
                'requested': self.quantity,
                'available': self.available_quantity
            })
    
    def _prepare_stock_move_values(self, picking):
        """Préparer les valeurs pour créer le mouvement de stock"""
        self.ensure_one()
        return {
            'name': self.product_id.name,
            'product_id': self.product_id.id,
            'product_uom_qty': self.quantity,
            'product_uom': self.product_uom_id.id,
            'picking_id': picking.id,
            'location_id': self.transfer_id.source_location_id.id,
            'location_dest_id': self.transfer_id.dest_location_id.id,
            'company_id': self.transfer_id.source_company_id.id,
        }

# Extension du modèle stock.picking pour ajouter la référence au transfert
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    transfer_id = fields.Many2one(
        'adi.stock.transfer',
        'Transfert Inter-Dépôts',
        index=True
    )
