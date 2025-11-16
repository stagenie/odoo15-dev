from odoo import fields, models, api




class AccountJournal(models.Model):
    _inherit = 'account.journal'

    qte_Journal = fields.Boolean(string="Inclure dans le calcul des quantités", default=True)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'   
    
    quantite_facturee = fields.Float(string="Quantité Facturée", compute='_compute_quantite_facturee', store=True)
    @api.depends('quantity', 'move_id.state', 'move_id.journal_id.qte_Journal')
    def _compute_quantite_facturee(self):
        for line in self:
            if line.move_id.state == 'posted' and line.move_id.journal_id.qte_Journal:
                line.quantite_facturee = line.quantity
            else:
                line.quantite_facturee = 0.0

    invoice_date = fields.Date(string="Date de Facturation", compute='_compute_invoice_date', store=True)

    @api.depends('move_id.invoice_date', 'move_id.date')
    def _compute_invoice_date(self):
        for line in self:
            # Utiliser invoice_date si disponible, sinon utiliser date (pour compatibilité)
            line.invoice_date = line.move_id.invoice_date or line.move_id.date

    





class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _force_recompute_qte_fields(self):
        """Force le recalcul des champs qte_af, qte_vf, et solde_qte."""        
        self.search([])._compute_qte()


    invoice_line_ids = fields.One2many(
        'account.move.line',  # Modèle cible
        'product_id',         # Champ inverse dans account.move.line
        string="Lignes de facture associées",
    ) 
     
    qte_af = fields.Float(string="Total Qté Facturée Fournisseur", compute="_compute_qte", store=True)
    qte_vf = fields.Float(string="Total Qté Facturée Clients", compute="_compute_qte", store=True)
    solde_qte = fields.Float(string="Solde Quantité", compute="_compute_qte", store=True)

    
    @api.depends('product_variant_ids',
             'product_variant_ids.invoice_line_ids.quantite_facturee',
             'product_variant_ids.invoice_line_ids.move_id.move_type')    
    def _compute_qte(self):
        for record in self:
            qte_fournisseur = 0.0
            qte_client = 0.0
            for variant in record.product_variant_ids:
                for line in variant.invoice_line_ids:
                    if line.move_id.move_type in ('in_invoice', 'in_refund'):
                        qte_fournisseur += line.quantite_facturee
                    elif line.move_id.move_type in ('out_invoice', 'out_refund'):
                        qte_client += line.quantite_facturee

            record.qte_af = qte_fournisseur
            record.qte_vf = qte_client
            record.solde_qte = qte_fournisseur - qte_client
    
    """ 
    @api.depends('invoice_line_ids.move_id.state', 'invoice_line_ids.quantity')
    def _compute_qte(self):
        for record in self:
            qte_fournisseur = 0.0
            qte_client = 0.0

            for line in record.invoice_line_ids:
                if line.move_id.state == 'posted' and line.move_id.journal_id.qte_Journal:
                    if line.move_id.move_type in ('in_invoice', 'in_refund'):
                        qte_fournisseur += line.quantity
                    elif line.move_id.move_type in ('out_invoice', 'out_refund'):
                        qte_client += line.quantity

            record.qte_af = qte_fournisseur
            record.qte_vf = qte_client
            record.solde_qte = qte_fournisseur - qte_client
    """

    def action_view_invoice_supplier(self):
        self.ensure_one()
        return {
            'name': 'Lignes de Facture Fournisseur',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'domain': [
                ('product_id', 'in', self.product_variant_ids.ids),
                #('product_id', '=', self.id),
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
                ('product_id', 'in', self.product_variant_ids.ids),
                # ('product_id', '=', self.id),
                ('move_id.move_type', 'in', ('out_invoice', 'out_refund')),
                ('move_id.state', '=', 'posted'),
                ('move_id.journal_id.qte_Journal', '=', True),  # Filtre par qte_Journal
            ],
            'context': {'create': False, 'edit': False},
            'views': [(self.env.ref('adi_quantity_invoiced.view_account_move_line_tree_custom').id, 'tree')],
        }

class ProductProduct(models.Model):
    _inherit = 'product.product'



    """def _force_recompute_qte_fields(self):
       
        self.search([])._compute_qte()
    """

    qte_af = fields.Float(string="Total Qté Facturée Fournisseur", compute='_compute_qte', store=True)
    qte_vf = fields.Float(string="Total Qté Facturée Clients", compute='_compute_qte', store=True)
    solde_qte = fields.Float(string="Solde Quantité", compute='_compute_qte', store=True)

    invoice_line_ids = fields.One2many(
        'account.move.line',
        'product_id',
        string="Lignes de facture associées",
    )
    

    @api.depends('invoice_line_ids.quantite_facturee', 'invoice_line_ids.move_id.move_type')
    def _compute_qte(self):
        for record in self:
            qte_fournisseur = 0.0
            qte_client = 0.0
            for line in record.invoice_line_ids:
                if line.move_id.move_type in ('in_invoice', 'in_refund'):
                    qte_fournisseur += line.quantite_facturee
                elif line.move_id.move_type in ('out_invoice', 'out_refund'):
                    qte_client += line.quantite_facturee

            record.qte_af = qte_fournisseur
            record.qte_vf = qte_client
            record.solde_qte = qte_fournisseur - qte_client
    """ 
     @api.depends('invoice_line_ids.move_id.state', 'invoice_line_ids.quantity')
    def _compute_qte(self):
        for record in self:
            qte_fournisseur = 0.0
            qte_client = 0.0

            for line in record.invoice_line_ids:
                if line.move_id.state == 'posted' and line.move_id.journal_id.qte_Journal:
                    if line.move_id.move_type in ('in_invoice', 'in_refund'):
                        qte_fournisseur += line.quantity
                    elif line.move_id.move_type in ('out_invoice', 'out_refund'):
                        qte_client += line.quantity

            record.qte_af = qte_fournisseur
            record.qte_vf = qte_client
            record.solde_qte = qte_fournisseur - qte_client
   
    """

   

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





