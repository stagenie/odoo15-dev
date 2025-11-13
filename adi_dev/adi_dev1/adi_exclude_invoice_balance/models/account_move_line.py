# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    exclude_from_partner_balance = fields.Boolean(
        string='Exclure du solde partenaire',
        default=False,
        help="Si coché, cette ligne ne sera pas prise en compte dans le calcul "
             "du solde du client/fournisseur."
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Hérite le champ exclude_from_partner_balance de account.move"""
        moves = self.env['account.move']
        for vals in vals_list:
            if vals.get('move_id') and not vals.get('exclude_from_partner_balance'):
                move = moves.browse(vals['move_id'])
                if move.exclude_from_partner_balance:
                    vals['exclude_from_partner_balance'] = True
        return super().create(vals_list)
