from odoo import fields, models, api

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    qte_Journal = fields.Boolean(string="Inclure dans le calcul des quantités", default=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    def _force_recompute_qte_fields(self):
        """Force le recalcul des champs qte_af, qte_vf, et solde_qte."""        
        self.search([])._compute_qte_af()
        self.search([])._compute_qte_vf()
        self.search([])._compute_solde_qte()


    invoice_line_ids = fields.One2many(
        'account.move.line',  # Modèle cible
        'product_id',         # Champ inverse dans account.move.line
        string="Lignes de facture associées",
    )

    
    qte_af = fields.Float(string="Total Qté Facturée Fournisseur", compute="_compute_qte_af", store=True)  
    qte_vf = fields.Float(string="Total Qté Facturée Clients", compute="_compute_qte_vf", store=True)
    solde_qte = fields.Float(string="Solde Quantité", compute="_compute_solde_qte", store=True)

    @api.depends('invoice_line_ids.move_id.journal_id.qte_Journal')  # Dépendance sur qte_Journa    
    def _compute_qte_af(self):
        for product in self:
            qte_af = sum(self.env['account.move.line'].search([
                ('product_id','=',product.id),
                ('move_id.move_type','in',('in_invoice','in_refund')),
                ('move_id.state','=','posted'),
                ('move_id.journal_id.qte_Journal', '=', True),  # Filtre par qte_Journal
            ]).mapped('quantity'))
            product.qte_af = qte_af
        
    @api.depends('invoice_line_ids.move_id.journal_id.qte_Journal')  # Dépendance sur qte_Journal    
    def _compute_qte_vf(self):
        for product in self:  
            qte_vf = sum(self.env['account.move.line'].search([
                ('product_id','=',product.id),
                ('move_id.move_type','in',('out_invoice','out_refund')),
                ('move_id.state','=','posted') ,
                ('move_id.journal_id.qte_Journal', '=', True),  # Filtre par qte_Journal
            ]).mapped('quantity'))
            product.qte_vf = qte_vf

    def _compute_solde_qte(self):
        for product in self:
            product.solde_qte = product.qte_af - product.qte_vf



    def action_view_invoice_supplier(self):
        self.ensure_one()
        return {
            'name': 'Lignes de Facture Fournisseur',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'domain': [
                ('product_id', '=', self.id),
                ('move_id.move_type', 'in', ('in_invoice', 'in_refund')),
                ('move_id.state', '=', 'posted'),
                ('move_id.journal_id.qte_Journal', '=', True),  # Filtre par qte_Journal
            ],
            'context': {'create': False, 'edit': False},
            'views': [(self.env.ref('adi_quantity_invoiced.view_account_move_line_tree_custom').id, 'tree')],
        }

    def action_view_invoice_customer(self):
        self.ensure_one()
        return {
            'name': 'Lignes de Facture Client',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'domain': [
                ('product_id', '=', self.id),
                ('move_id.move_type', 'in', ('out_invoice', 'out_refund')),
                ('move_id.state', '=', 'posted'),
                ('move_id.journal_id.qte_Journal', '=', True),  # Filtre par qte_Journal
            ],
            'context': {'create': False, 'edit': False},
            'views': [(self.env.ref('adi_quantity_invoiced.view_account_move_line_tree_custom').id, 'tree')],
        }


class ProductProduct(models.Model):
    _inherit = 'product.product'
    # Champs liés à ceux de product.template
    qte_af = fields.Float(related='product_tmpl_id.qte_af', store=True, readonly=False)
    qte_vf = fields.Float(related='product_tmpl_id.qte_vf', store=True, readonly=False)
    solde_qte = fields.Float(related='product_tmpl_id.solde_qte', store=True, readonly=False)

    def action_view_invoice_supplier(self):
        self.ensure_one()
        return {
            'name': 'Lignes de Facture Fournisseur',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'domain': [
                ('product_id', '=', self.id),
                ('move_id.move_type', 'in', ('in_invoice', 'in_refund')),
                ('move_id.state', '=', 'posted'),
                ('move_id.journal_id.qte_Journal', '=', True),  # Filtre par qte_Journal
            ],
            'context': {'create': False, 'edit': False},
            'views': [(self.env.ref('adi_quantity_invoiced.view_account_move_line_tree_custom').id, 'tree')],
        }

    def action_view_invoice_customer(self):
        self.ensure_one()
        return {
            'name': 'Lignes de Facture Client',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'domain': [
                ('product_id', '=', self.id),
                ('move_id.move_type', 'in', ('out_invoice', 'out_refund')),
                ('move_id.state', '=', 'posted'),
                ('move_id.journal_id.qte_Journal', '=', True),  # Filtre par qte_Journal
            ],
            'context': {'create': False, 'edit': False},
            'views': [(self.env.ref('adi_quantity_invoiced.view_account_move_line_tree_custom').id, 'tree')],
        }






""""

class ProductProduct(models.Model):
    _inherit = 'product.product'

    invoice_line_ids = fields.One2many(
        'account.move.line',  # Modèle cible
        'product_id',         # Champ inverse dans account.move.line
        string="Lignes de facture associées",
    )

    qte_af = fields.Float(string="Total Qté Facturée Fournisseur", compute="_compute_qte_af", store=True)
    qte_vf = fields.Float(string="Total Qté Facturée Clients", compute="_compute_qte_vf", store=True)
    solde_qte = fields.Float(string="Solde Quantité", compute="_compute_solde_qte", store=True)

    @api.depends('invoice_line_ids.quantity', 'invoice_line_ids.move_id.state', 'invoice_line_ids.move_id.journal_id.qte_Journal')    
    def _compute_qte_af(self):
        for product in self:
            lines = self.env['account.move.line'].search([
                ('product_id', '=', product.id),
                ('move_id.move_type', 'in', ('in_invoice', 'in_refund')),
                ('move_id.state', '=', 'posted'),
                ('move_id.journal_id.qte_Journal', '=', True),
            ])
            qte_af = sum(lines.mapped('quantity'))
            product.qte_af = qte_af

    @api.depends('invoice_line_ids.quantity', 'invoice_line_ids.move_id.state', 'invoice_line_ids.move_id.journal_id.qte_Journal')
    def _compute_qte_vf(self):
        for product in self:
            lines = self.env['account.move.line'].search([
                ('product_id', '=', product.id),
                ('move_id.move_type', 'in', ('out_invoice', 'out_refund')),
                ('move_id.state', '=', 'posted'),
                ('move_id.journal_id.qte_Journal', '=', True),
            ])
            qte_vf = sum(lines.mapped('quantity'))
            product.qte_vf = qte_vf

    def _compute_solde_qte(self):
        for product in self:
            product.solde_qte = product.qte_af - product.qte_vf

    def action_view_invoice_customer(self):
        self.ensure_one()
        return {
            'name': 'Lignes de Facture Client',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'domain': [
                ('product_id', '=', self.id),
                ('move_id.move_type', 'in', ('out_invoice', 'out_refund')),
                ('move_id.state', '=', 'posted'),
                ('move_id.journal_id.qte_Journal', '=', True),  # Filtre par qte_Journal
            ],
            'context': {'create': False, 'edit': False},
            'views': [(self.env.ref('adi_quantity_invoiced.view_account_move_line_tree_custom').id, 'tree')],
        }


    def action_view_invoice_supplier(self):
        self.ensure_one()
        return {
            'name': 'Lignes de Facture Fournisseur',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'domain': [
                ('product_id', '=', self.id),
                ('move_id.move_type', 'in', ('in_invoice', 'in_refund')),
                ('move_id.state', '=', 'posted'),
                ('move_id.journal_id.qte_Journal', '=', True),  # Filtre par qte_Journal
            ],
            'context': {'create': False, 'edit': False},
            'views': [(self.env.ref('adi_quantity_invoiced.view_account_move_line_tree_custom').id, 'tree')],
        }

"""

