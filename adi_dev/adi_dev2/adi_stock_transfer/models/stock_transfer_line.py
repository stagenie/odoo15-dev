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
        'Quantité à Transférer',
        required=True,
        digits='Product Unit of Measure',
        default=1.0
    )
    
    available_quantity = fields.Float(
        'Quantité Disponible',
        compute='_compute_available_quantity',
        digits='Product Unit of Measure',
        store=False
    )
    
    note = fields.Text('Notes')
    
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
        """Vérification que la quantité est positive"""
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_("La quantité doit être strictement positive!"))
    
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
