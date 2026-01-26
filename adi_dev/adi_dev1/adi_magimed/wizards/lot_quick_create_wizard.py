# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class LotQuickCreateWizard(models.TransientModel):
    _name = 'lot.quick.create.wizard'
    _description = 'Assistant Creation Rapide de Lot'

    product_id = fields.Many2one(
        'product.product',
        string='Produit',
        required=True
    )
    lot_name = fields.Char(
        string='Numero de Lot',
        required=True
    )
    expiration_date = fields.Datetime(
        string='Date d\'Expiration'
    )
    use_date = fields.Datetime(
        string='Date Limite d\'Utilisation Optimale'
    )
    removal_date = fields.Datetime(
        string='Date de Retrait'
    )
    alert_date = fields.Datetime(
        string='Date d\'Alerte'
    )
    ref = fields.Char(
        string='Reference Interne'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Societe',
        default=lambda self: self.env.company
    )
    move_line_id = fields.Many2one(
        'stock.move.line',
        string='Ligne de Mouvement'
    )
    auto_generate_name = fields.Boolean(
        string='Generer Numero Automatiquement',
        default=False
    )

    @api.onchange('auto_generate_name', 'product_id')
    def _onchange_auto_generate(self):
        if self.auto_generate_name and self.product_id:
            self.lot_name = self.env['stock.production.lot'].generate_lot_name(self.product_id)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            # Set defaults from product
            if self.product_id.use_expiration_date:
                # Could set default expiration based on product settings
                pass
            if self.product_id.auto_lot_on_receipt:
                self.auto_generate_name = True
                self.lot_name = self.env['stock.production.lot'].generate_lot_name(self.product_id)

    def action_create_lot(self):
        """Create the lot and optionally assign to move line"""
        self.ensure_one()

        if not self.lot_name:
            raise UserError(_('Le numero de lot est obligatoire.'))

        # Check if lot already exists
        existing = self.env['stock.production.lot'].search([
            ('name', '=', self.lot_name),
            ('product_id', '=', self.product_id.id),
            ('company_id', '=', self.company_id.id)
        ], limit=1)

        if existing:
            raise UserError(_('Un lot avec ce numero existe deja pour ce produit.'))

        # Create lot
        lot_vals = {
            'name': self.lot_name,
            'product_id': self.product_id.id,
            'company_id': self.company_id.id,
            'ref': self.ref,
        }

        if self.expiration_date:
            lot_vals['expiration_date'] = self.expiration_date
        if self.use_date:
            lot_vals['use_date'] = self.use_date
        if self.removal_date:
            lot_vals['removal_date'] = self.removal_date
        if self.alert_date:
            lot_vals['alert_date'] = self.alert_date

        lot = self.env['stock.production.lot'].create(lot_vals)

        # Assign to move line if provided
        if self.move_line_id:
            self.move_line_id.write({'lot_id': lot.id})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.production.lot',
            'res_id': lot.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_create_and_close(self):
        """Create lot and close wizard"""
        self.ensure_one()

        if not self.lot_name:
            raise UserError(_('Le numero de lot est obligatoire.'))

        existing = self.env['stock.production.lot'].search([
            ('name', '=', self.lot_name),
            ('product_id', '=', self.product_id.id),
            ('company_id', '=', self.company_id.id)
        ], limit=1)

        if existing:
            raise UserError(_('Un lot avec ce numero existe deja pour ce produit.'))

        lot_vals = {
            'name': self.lot_name,
            'product_id': self.product_id.id,
            'company_id': self.company_id.id,
            'ref': self.ref,
        }

        if self.expiration_date:
            lot_vals['expiration_date'] = self.expiration_date
        if self.use_date:
            lot_vals['use_date'] = self.use_date
        if self.removal_date:
            lot_vals['removal_date'] = self.removal_date
        if self.alert_date:
            lot_vals['alert_date'] = self.alert_date

        lot = self.env['stock.production.lot'].create(lot_vals)

        if self.move_line_id:
            self.move_line_id.write({'lot_id': lot.id})

        return {'type': 'ir.actions.act_window_close'}
