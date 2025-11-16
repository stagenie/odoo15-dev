from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_total_due = fields.Boolean("Afficher le total échu", config_parameter='mai_customer_overdue_balance.show_total_due')
    show_total_balance = fields.Boolean("Afficher le solde total", config_parameter='mai_customer_overdue_balance.show_total_balance')
    show_previous_balance = fields.Boolean("Afficher l'ancien solde", config_parameter='mai_customer_overdue_balance.show_previous_balance')

class ResCompany(models.Model):
    _inherit = 'res.company'

    show_total_due = fields.Boolean(compute='_compute_show_total_due', inverse='_set_show_total_due')
    show_total_balance = fields.Boolean(compute='_compute_show_total_balance', inverse='_set_show_total_balance')
    show_previous_balance = fields.Boolean(compute='_compute_show_previous_balance', inverse='_set_show_previous_balance')

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

    def _compute_show_previous_balance(self):
        for company in self:
            company.show_previous_balance = self.env['ir.config_parameter'].sudo().get_param('mai_customer_overdue_balance.show_previous_balance', default=False)

    def _set_show_previous_balance(self):
        self.env['ir.config_parameter'].sudo().set_param('mai_customer_overdue_balance.show_previous_balance', self.show_previous_balance)

    

# Nouvelle méthode plus exacte 

class ResPartner(models.Model):
    _inherit = 'res.partner'

    overdue_amount = fields.Float(compute='_compute_amount', string='Montant Échu')
    balance_due = fields.Float(compute='_compute_amount', string='Solde Actuel')
    previous_balance = fields.Float(compute='_compute_amount', string='Ancien Solde')

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
            previous_balance = 0.0
            current_balance = 0.0

            # Récupérer toutes les factures impayées du partenaire
            invoices = self.env['account.move'].search([
                ('partner_id', '=', record.id),
                ('state', '=', 'posted'),
                ('move_type', '=', 'out_invoice'),
                ('payment_state', '!=', 'paid')
            ], order='invoice_date asc, id asc')

            if invoices:
                # Identifier la facture courante (la plus récente)
                current_invoice = invoices[-1]

                # Ancien solde : factures non payées AVANT la facture courante
                previous_invoices = invoices.filtered(lambda inv: inv.invoice_date < current_invoice.invoice_date)
                previous_balance = sum(previous_invoices.mapped('amount_residual'))

                overdue_invoices = invoices.filtered(lambda inv: inv.invoice_date_due and inv.invoice_date_due < current_date)
                total_overdue_amount = sum(overdue_invoices.mapped('amount_residual'))


            # Récupérer toutes les lignes comptables pour le solde total
            all_move_lines = account_move_line_obj.search([
                ('partner_id', '=', record.id),
                ('account_id.internal_type', '=', 'receivable'),
                ('move_id.state', '=', 'posted'),
            ])

            # Calculer le solde total et le montant échu
            for line in all_move_lines:
                total_balance_due += line.balance                           
           

            # Affectation des valeurs aux champs
            record.previous_balance = previous_balance
            record.balance_due = total_balance_due
            record.overdue_amount = total_overdue_amount

# Fin nouvelle méthode 

""" 
Ancien méthode
class ResPartner(models.Model):
    _inherit = 'res.partner'

    overdue_amount = fields.Float(compute='_compute_amount', string='Montant Échu')
    balance_due = fields.Float(compute='_compute_amount', string='Total Solde')
    previous_balance = fields.Float(compute='_compute_amount', string='Ancien Solde')
    
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
            previous_balance = 0.0

            # Pour la facture courante
            current_invoice = self.env['account.move'].search([
                ('id', 'in', record.invoice_ids.ids),
                ('state', '=', 'posted'),
                ('move_type', '=', 'out_invoice')
            ], order='invoice_date desc', limit=1)

            if current_invoice:
                # Récupérer toutes les lignes comptables antérieures à la facture courante
                previous_move_lines = account_move_line_obj.search([
                    ('partner_id', '=', record.id),
                    ('account_id.internal_type', '=', 'receivable'),
                    ('move_id.state', '=', 'posted'),
                    ('move_id.invoice_date', '<', current_invoice.invoice_date),
                ])

                # Calculer l'ancien solde (somme des soldes des factures antérieures)
                for line in previous_move_lines:
                    previous_balance += line.balance

                # Récupérer toutes les lignes comptables pour le solde total
                all_move_lines = account_move_line_obj.search([
                    ('partner_id', '=', record.id),
                    ('account_id.internal_type', '=', 'receivable'),
                    ('move_id.state', '=', 'posted'),
                ])

                # Calculer le solde total et le montant échu
                for line in all_move_lines:
                    total_balance_due += line.balance
                    if line.date_maturity and line.date_maturity < current_date:
                        total_overdue_amount += line.balance

            record.previous_balance = previous_balance
            record.balance_due = total_balance_due
            record.overdue_amount = total_overdue_amount

""" 
