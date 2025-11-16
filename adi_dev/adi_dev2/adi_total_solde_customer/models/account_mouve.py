from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    client_solde_total = fields.Monetary(string="Solde Total Client", compute='_compute_client_solde_total', store=True)

    @api.depends('partner_id', 'date')
    def _compute_client_solde_total(self):
        for move in self:
            if move.partner_id:
                # Calcul du solde initial depuis le journal d'ouverture
                solde_initial = 0.0
                opening_move = self.env['account.move'].search([
                    ('journal_id.type', '=', 'general'),
                    ('date', '<', move.date),
                    ('partner_id', '=', move.partner_id.id),
                    ('line_ids.account_id.user_type_id.type', '=', 'receivable') # Comptes clients
                ])
                for om in opening_move:
                    for line in om.line_ids:
                        if line.account_id.user_type_id.type == 'receivable':
                            solde_initial += line.debit - line.credit
                

                # Calcul des mouvements depuis le journal des ventes (et autres journaux pertinents)
                mouvements = self.env['account.move.line'].search([
                    ('partner_id', '=', move.partner_id.id),
                    ('date', '<', move.date),
                    ('account_id.user_type_id.type', '=', 'receivable')
                ])

                solde_mouvements = sum(m.debit - m.credit for m in mouvements)
                move.client_solde_total = solde_initial + solde_mouvements

            else:
                move.client_solde_total = 0.0