# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    synced_invoice_ids = fields.Many2many(
        'account.move',
        'account_move_sync_rel',
        'source_move_id',
        'target_move_id',
        string='Factures synchronisées',
        help="Factures dont les lignes ont été importées (traçabilité uniquement).",
        copy=False,
    )

    def action_open_invoice_sync_wizard(self):
        """Ouvre le wizard de synchronisation des factures"""
        self.ensure_one()

        return {
            'name': _('Ajouter des lignes depuis des factures'),
            'type': 'ir.actions.act_window',
            'res_model': 'invoice.line.sync.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_invoice_id': self.id,
            }
        }
