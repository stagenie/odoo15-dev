# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_send_whatsapp(self):
        """Ouvre le wizard d'envoi WhatsApp"""
        self.ensure_one()

        return {
            'name': _('Envoyer via WhatsApp'),
            'type': 'ir.actions.act_window',
            'res_model': 'whatsapp.send.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_model': self._name,
                'active_id': self.id,
                'default_res_model': self._name,
                'default_res_id': self.id,
            },
        }
