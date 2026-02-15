# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class MagimedExpiryConfirmation(models.TransientModel):
    _name = 'magimed.expiry.confirmation'
    _description = 'Confirmation Expiration MAGIMED'

    picking_ids = fields.Many2many(
        'stock.picking',
        string='Transferts',
    )
    lot_ids = fields.Many2many(
        'stock.production.lot',
        string='Lots expires',
    )
    description = fields.Text(
        string='Details',
        readonly=True,
    )

    def button_confirm(self):
        """Confirm validation despite expired lots"""
        self.ensure_one()
        return self.picking_ids.with_context(
            skip_magimed_expiry=True,
        ).button_validate()

    def button_cancel(self):
        """Cancel and go back"""
        return {'type': 'ir.actions.act_window_close'}
