from odoo import api, fields, models

class ProductSaleHistory(models.TransientModel):
    _name = 'product.sale.history.wizard'
    _description = 'Historique des prix de vente'

    product_id = fields.Many2one('product.product', string='Produit', readonly=True)
    sale_history_ids = fields.One2many('product.sale.history.line', 'wizard_id', string='Historique')
    
    # Ajout des champs de filtre
    date_from = fields.Date(string='Date début')
    date_to = fields.Date(string='Date fin')
    state = fields.Selection([
        ('draft', 'Devis'),
        ('sent', 'Devis envoyé'),
        ('sale', 'Bon de commande'),
        ('done', 'Verrouillé'),
        ('cancel', 'Annulé'),
    ], string='État', default='sale')
    salesperson_id = fields.Many2one('res.users', string='Vendeur')
    team_id = fields.Many2one('crm.team', string='Équipe commerciale')

    @api.onchange('date_from', 'date_to', 'state', 'salesperson_id', 'team_id')
    def _onchange_filters(self):
        domain = [
            ('product_id', '=', self.product_id.id),
            ('id', '!=', self._context.get('active_line_id'))
        ]

        if self.date_from:
            domain.append(('order_id.date_order', '>=', self.date_from))
        if self.date_to:
            domain.append(('order_id.date_order', '<=', self.date_to))
        if self.state:
            domain.append(('order_id.state', '=', self.state))
        if self.salesperson_id:
            domain.append(('order_id.user_id', '=', self.salesperson_id.id))
        if self.team_id:
            domain.append(('order_id.team_id', '=', self.team_id.id))

        historical_sales = self.env['sale.order.line'].sudo().search(domain, order='create_date desc')

        # Supprime les anciennes lignes
        self.sale_history_ids.unlink()
        
        # Crée les nouvelles lignes filtrées
        vals = []
        for line in historical_sales:
            vals.append((0, 0, {
                'order_id': line.order_id.id,
                'date_order': line.order_id.date_order,
                'price_unit': line.price_unit,
                'discount': line.discount,  # Ajout de la remise
                'salesperson_id': line.order_id.user_id.id,
                'team_id': line.order_id.team_id.id,
                'state': line.order_id.state,
            }))
        self.sale_history_ids = vals

class ProductSaleHistoryLine(models.TransientModel):
    _name = 'product.sale.history.line'
    _description = 'Ligne d\'historique des ventes'

    wizard_id = fields.Many2one('product.sale.history.wizard')
    order_id = fields.Many2one('sale.order', string='Commande', readonly=True)
    date_order = fields.Datetime(string='Date', readonly=True)
    price_unit = fields.Float(string='Prix unitaire', readonly=True)
    discount = fields.Float(string='Remise (%)', readonly=True)  # Ajout du champ remise
    salesperson_id = fields.Many2one('res.users', string='Vendeur', readonly=True)
    team_id = fields.Many2one('crm.team', string='Équipe commerciale', readonly=True)
    state = fields.Selection([
        ('draft', 'Devis'),
        ('sent', 'Devis envoyé'),
        ('sale', 'Bon de commande'),
        ('done', 'Verrouillé'),
        ('cancel', 'Annulé'),
    ], string='État', readonly=True)