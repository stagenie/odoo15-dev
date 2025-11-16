from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    total_balance = fields.Monetary(
        string="Total Balance",
        compute="_compute_total_balance",
        currency_field="currency_id",
        store=True,
    )

    @api.depends('credit', 'debit', 'move_line_ids.balance', 'move_line_ids.move_id.state')
    def _compute_total_balance(self):
        for partner in self:
            # Obtenir toutes les lignes comptables postées associées au partenaire
            lines = self.env['account.move.line'].search([
                ('partner_id', '=', partner.id),
                ('move_id.state', '=', 'posted'),
            ])
            # Calculer le solde total
            partner.total_balance = sum(lines.mapped('balance'))
