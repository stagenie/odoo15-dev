# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockTransferConfirmDoneWizard(models.TransientModel):
    """Wizard de confirmation pour terminer un transfert avec réception complète"""
    _name = 'adi.stock.transfer.confirm.done.wizard'
    _description = 'Confirmation de Réception Complète'

    transfer_id = fields.Many2one(
        'adi.stock.transfer',
        'Transfert',
        required=True,
        readonly=True
    )

    def action_confirm(self):
        """Confirmer et terminer le transfert avec réception complète"""
        self.ensure_one()
        self.transfer_id.action_done_confirmed()
        return {'type': 'ir.actions.act_window_close'}
