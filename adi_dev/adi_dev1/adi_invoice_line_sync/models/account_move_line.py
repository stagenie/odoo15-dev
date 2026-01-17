# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    source_invoice_id = fields.Many2one(
        'account.move',
        string='Facture source',
        copy=False,
        readonly=True,
        help="Indique de quelle facture cette ligne a été synchronisée."
    )

    is_synced_line = fields.Boolean(
        string='Ligne synchronisée',
        compute='_compute_is_synced_line',
        store=True,
        help="Indique si cette ligne provient d'une synchronisation."
    )

    @api.depends('source_invoice_id')
    def _compute_is_synced_line(self):
        for line in self:
            line.is_synced_line = bool(line.source_invoice_id)
