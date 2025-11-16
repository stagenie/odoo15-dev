from odoo import api, fields, models

#aFFICHER OU PAS LE TOTAL ECHU ET SOLDE ACTUEL

 

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_total_due = fields.Boolean("Afficher le total échu", config_parameter='mai_customer_overdue_balance.show_total_due')
    show_total_balance = fields.Boolean("Afficher le solde total", config_parameter='mai_customer_overdue_balance.show_total_balance')

class ResCompany(models.Model):
    _inherit = 'res.company'

    show_total_due = fields.Boolean(compute='_compute_show_total_due', inverse='_set_show_total_due')
    show_total_balance = fields.Boolean(compute='_compute_show_total_balance', inverse='_set_show_total_balance')

    def _compute_show_total_due(self):
        for company in self:
            company.show_total_due = self.env['ir.config_parameter'].sudo().get_param('mai_customer_overdue_balance.show_total_due', default=False)

    def _set_show_total_due(self):
        self.env['ir.config_parameter'].sudo().set_param('mai_customer_overdue_balance.show_total_due', self.show_total_due)

    def _compute_show_total_balance(self):
        for company in self:
            company.show_total_balance = self.env['ir.config_parameter'].sudo().get_param('mai_customer_overdue_balance.show_total_balance', default=False)

    def _set_show_total_balance(self):
        self.env['ir.config_parameter'].sudo().set_param('mai_customer_overdue_balance.show_total_balance', self.show_total_balance)





class ResPartner(models.Model):
    _inherit = 'res.partner'

    overdue_amount = fields.Float(compute='_compute_amount', string='Montant Échu')
    balance_due = fields.Float(compute='_compute_amount', string='Total Solde')
    
    invoice_ids = fields.One2many(
        'account.move', 
        'partner_id', 
        domain=[('move_type', '=', 'out_invoice'), ('state', '=', 'posted'), ('payment_state', '!=', 'paid')]
    )

    @api.depends('invoice_ids', 'invoice_ids.state', 'invoice_ids.invoice_date', 'invoice_ids.invoice_date_due')
    def _compute_amount(self):
        account_move_line_obj = self.env['account.move.line']
        for record in self:
            current_date = fields.Date.today()
            total_overdue_amount = 0.0
            total_balance_due = 0.0

            # Récupérer toutes les lignes comptables liées au partenaire
            move_lines = account_move_line_obj.search([
                ('partner_id', '=', record.id),
                ('account_id.internal_type', '=', 'receivable'),
                ('move_id.state', '=', 'posted'),
            ])

            for line in move_lines:
                total_balance_due += line.balance
                if line.date_maturity and line.date_maturity < current_date:
                    total_overdue_amount += line.balance

            record.overdue_amount = total_overdue_amount
            record.balance_due = total_balance_due


    # Méthode plus exacte : 
    @api.depends('invoice_ids', 'invoice_ids.state', 'invoice_ids.invoice_date', 'invoice_ids.invoice_date_due')
    def _compute_amount(self):
        account_move_line_obj = self.env['account.move.line']
        for record in self:
            current_date = fields.Date.today()
            total_overdue_amount = 0.0
            total_balance_due = 0.0
            previous_balance = 0.0

            # Pour la facture courante
            current_invoice = self.env['account.move'].search([
                ('id', 'in', record.invoice_ids.ids),
                ('state', '=', 'posted'),
                ('move_type', '=', 'out_invoice')
            ], order='create_date desc', limit=1)

            if current_invoice:
                # Récupérer toutes les lignes comptables antérieures à la facture courante
                previous_move_lines = account_move_line_obj.search([
                    ('partner_id', '=', record.id),
                    ('account_id.internal_type', '=', 'receivable'),
                    ('move_id.state', '=', 'posted'),
                    ('move_id.create_date', '<', current_invoice.create_date),
                ])

                # Calculer l'ancien solde
                for line in previous_move_lines:
                    previous_balance += line.balance

                # Pour le total échu, on prend en compte toutes les factures dont la date d'échéance est dépassée
                overdue_move_lines = account_move_line_obj.search([
                    ('partner_id', '=', record.id),
                    ('account_id.internal_type', '=', 'receivable'),
                    ('move_id.state', '=', 'posted'),
                    ('date_maturity', '<', current_date),
                ])

                # Pour le solde actuel, on prend toutes les factures jusqu'à la date actuelle
                current_move_lines = account_move_line_obj.search([
                    ('partner_id', '=', record.id),
                    ('account_id.internal_type', '=', 'receivable'),
                    ('move_id.state', '=', 'posted'),
                ])

                # Calcul du total échu
                for line in overdue_move_lines:
                    total_overdue_amount += line.balance

                # Calcul du solde actuel
                for line in current_move_lines:
                    total_balance_due += line.balance

            record.previous_balance = previous_balance
            record.balance_due = total_balance_due
            record.overdue_amount = total_overdue_amount
