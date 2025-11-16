from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = "product.product"

    total_saled = fields.Float(
        string="Total Vendue",
        compute="_compute_total_saled",
        store=True
    )
    total_purchased = fields.Float(
        string="Total Acheté",
        compute="_compute_total_purchased",
        store=True
    )
    balance_av = fields.Float(
        string="Solde A-V",
        compute="_compute_balance_av",
        store=True
    )

    @api.depends()
    def _compute_total_saled(self):
        for product in self:
            # Recherche des lignes de factures pour ce produit spécifique
            invoices = self.env['account.move.line'].search([
                ('product_id', '=', product.id),
                ('move_id.journal_id.chek_quantity_saled', '=', True),
                ('move_id.state', '=', 'posted')  # Optionnel : uniquement les factures validées
            ])
            product.total_saled = sum(invoices.mapped('quantity'))

    @api.depends()
    def _compute_total_purchased(self):
        for product in self:
            # Recherche des lignes de factures pour ce produit spécifique
            invoices = self.env['account.move.line'].search([
                ('product_id', '=', product.id),
                ('move_id.journal_id.chek_quantity_purchased', '=', True),
                ('move_id.state', '=', 'posted')  # Optionnel : uniquement les factures validées
            ])
            product.total_purchased = sum(invoices.mapped('quantity'))

    @api.depends('total_saled', 'total_purchased')
    def _compute_balance_av(self):
        for product in self:
            product.balance_av = product.total_purchased - product.total_saled

    def action_view_customer_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Factures Clients',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [
                ('invoice_line_ids.product_id', '=', self.id),
                ('journal_id.check_quantity_saled', '=', True),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted')
            ],
            'context': {'default_move_type': 'out_invoice'},
        }

    def action_view_supplier_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Factures Fournisseurs',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [
                ('invoice_line_ids.product_id', '=', self.id),
                ('journal_id.check_quantity_purchased', '=', True),
                ('move_type', '=', 'in_invoice'),
                ('state', '=', 'posted')
            ],
            'context': {'default_move_type': 'in_invoice'},
        }

class ProductTemplate(models.Model):
    _inherit = "product.template"

    total_saled = fields.Float(
        string="Total Vendue",
        compute="_compute_total_saled",
        store=True
    )
    total_purchased = fields.Float(
        string="Total Acheté",
        compute="_compute_total_purchased",
        store=True
    )
    balance_av = fields.Float(
        string="Solde A-V",
        compute="_compute_balance_av",
        store=True
    )

    @api.depends()
    def _compute_total_saled(self):
        for template in self:
            # Recherche des lignes de factures pour toutes les variantes du template
            invoices = self.env['account.move.line'].search([
                ('product_id', 'in', template.product_variant_ids.ids),
                ('move_id.journal_id.chek_quantity_saled', '=', True),
                ('move_id.state', '=', 'posted')  # Optionnel : uniquement les factures validées
            ])
            template.total_saled = sum(invoices.mapped('quantity'))

    @api.depends()
    def _compute_total_purchased(self):
        for template in self:
            # Recherche des lignes de factures pour toutes les variantes du template
            invoices = self.env['account.move.line'].search([
                ('product_id', 'in', template.product_variant_ids.ids),
                ('move_id.journal_id.chek_quantity_purchased', '=', True),
                ('move_id.state', '=', 'posted')  # Optionnel : uniquement les factures validées
            ])
            template.total_purchased = sum(invoices.mapped('quantity'))

    @api.depends('total_saled', 'total_purchased')
    def _compute_balance_av(self):
        for template in self:
            template.balance_av = template.total_purchased - template.total_saled
            
    def action_view_customer_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Factures Clients',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [
                ('invoice_line_ids.product_id', 'in', self.product_variant_ids.ids),
                ('journal_id.check_quantity_saled', '=', True),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted')
            ],
            'context': {'default_move_type': 'out_invoice'},
        }

    def action_view_supplier_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Factures Fournisseurs',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [
                ('invoice_line_ids.product_id', 'in', self.product_variant_ids.ids),
                ('journal_id.check_quantity_purchased', '=', True),
                ('move_type', '=', 'in_invoice'),
                ('state', '=', 'posted')
            ],
            'context': {'default_move_type': 'in_invoice'},
        }