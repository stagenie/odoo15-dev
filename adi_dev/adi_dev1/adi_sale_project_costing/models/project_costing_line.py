# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProjectCostingLine(models.Model):
    _name = 'project.costing.line'
    _description = 'Ligne de calcul costing projet'
    _order = 'sequence, id'

    # ====== RELATIONS ======
    order_id = fields.Many2one(
        'sale.order',
        string='Devis/Commande',
        required=True,
        ondelete='cascade',
        index=True
    )

    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Ligne de devis liée',
        ondelete='set null',
        domain="[('order_id', '=', order_id)]",
        help="Ligne de devis à synchroniser avec ce calcul"
    )

    sequence = fields.Integer(string='Séquence', default=10)

    # ====== PRODUIT ======
    product_id = fields.Many2one(
        'product.product',
        string='Produit',
        required=True,
        domain="[('sale_ok', '=', True)]"
    )

    name = fields.Char(
        string='Description',
        compute='_compute_name',
        store=True
    )

    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unité',
        related='product_id.uom_id',
        readonly=True
    )

    # ====== QUANTITE ======
    quantity = fields.Float(
        string='Quantité',
        required=True,
        default=1.0,
        digits='Product Unit of Measure'
    )

    # ====== PRIX D'ACHAT (COUT) ======
    purchase_price = fields.Float(
        string="Prix d'achat (Coût)",
        digits='Product Price',
        compute='_compute_purchase_price',
        store=True,
        readonly=False,
        help="Prix d'achat unitaire (coût standard du produit)"
    )

    # ====== MARGES EN POURCENTAGE ======
    equipment_margin_percent = fields.Float(
        string='% Marge Équipement',
        digits=(16, 2),
        default=0.0,
        help="Pourcentage de marge équipement (ex: 15, 20)"
    )

    labor_margin_percent = fields.Float(
        string="% Main d'Oeuvre",
        digits=(16, 2),
        default=0.0,
        help="Pourcentage main d'oeuvre (ex: 20, 30, 80)"
    )

    # ====== CALCULS AUTOMATIQUES ======
    total_margin_percent = fields.Float(
        string='% Marge Totale',
        compute='_compute_margins',
        store=True,
        help="Somme des pourcentages (Équipement + M.O.)"
    )

    equipment_margin_amount = fields.Float(
        string='Montant Marge Équipement',
        compute='_compute_margins',
        store=True,
        digits='Product Price'
    )

    labor_margin_amount = fields.Float(
        string="Montant Main d'Oeuvre",
        compute='_compute_margins',
        store=True,
        digits='Product Price'
    )

    # Prix de vente unitaire calculé
    sale_price_unit = fields.Float(
        string='Prix de Vente Unitaire',
        compute='_compute_margins',
        store=True,
        digits='Product Price',
        help="Coût × (1 + %Équipement + %M.O.)"
    )

    # ====== SOUS-TOTAUX ======
    subtotal_cost = fields.Monetary(
        string='Sous-total Coût',
        compute='_compute_subtotals',
        store=True,
        currency_field='currency_id'
    )

    subtotal_sale = fields.Monetary(
        string='Sous-total Vente',
        compute='_compute_subtotals',
        store=True,
        currency_field='currency_id'
    )

    margin_total = fields.Monetary(
        string='Marge Totale',
        compute='_compute_subtotals',
        store=True,
        currency_field='currency_id',
        help="Différence entre prix de vente et coût"
    )

    total_equipment_margin = fields.Monetary(
        string='Total Marge Équipement',
        compute='_compute_subtotals',
        store=True,
        currency_field='currency_id'
    )

    total_labor_margin = fields.Monetary(
        string="Total Main d'Oeuvre",
        compute='_compute_subtotals',
        store=True,
        currency_field='currency_id'
    )

    # ====== CHAMPS TECHNIQUES ======
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        related='order_id.currency_id',
        readonly=True
    )

    order_state = fields.Selection(
        related='order_id.state',
        string='État commande',
        readonly=True
    )

    is_synced = fields.Boolean(
        string='Synchronisé',
        default=False,
        help="Indique si le prix a été synchronisé vers la ligne de devis"
    )

    last_sync_date = fields.Datetime(
        string='Dernière synchronisation',
        readonly=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        related='order_id.company_id',
        store=True,
        readonly=True
    )

    # ====== METHODES COMPUTE ======

    @api.depends('product_id')
    def _compute_name(self):
        for line in self:
            if line.product_id:
                line.name = line.product_id.display_name
            else:
                line.name = ''

    @api.depends('product_id', 'product_id.standard_price')
    def _compute_purchase_price(self):
        """Récupère le prix d'achat (standard_price) du produit"""
        for line in self:
            if line.product_id:
                line.purchase_price = line.product_id.standard_price
            else:
                line.purchase_price = 0.0

    @api.depends('purchase_price', 'equipment_margin_percent', 'labor_margin_percent')
    def _compute_margins(self):
        """Calcule les marges et le prix de vente unitaire

        Formule: Prix Vente = Coût × (1 + %Équipement/100 + %M.O./100)
        """
        for line in self:
            cost = line.purchase_price or 0.0
            eq_pct = (line.equipment_margin_percent or 0.0) / 100.0
            labor_pct = (line.labor_margin_percent or 0.0) / 100.0

            # Total marge en %
            line.total_margin_percent = (line.equipment_margin_percent or 0.0) + (line.labor_margin_percent or 0.0)

            # Montants des marges unitaires
            line.equipment_margin_amount = cost * eq_pct
            line.labor_margin_amount = cost * labor_pct

            # Prix de vente unitaire
            line.sale_price_unit = cost * (1 + eq_pct + labor_pct)

    @api.depends('quantity', 'purchase_price', 'sale_price_unit',
                 'equipment_margin_amount', 'labor_margin_amount')
    def _compute_subtotals(self):
        """Calcule les sous-totaux"""
        for line in self:
            qty = line.quantity or 0.0
            line.subtotal_cost = qty * (line.purchase_price or 0.0)
            line.subtotal_sale = qty * (line.sale_price_unit or 0.0)
            line.margin_total = line.subtotal_sale - line.subtotal_cost
            line.total_equipment_margin = qty * (line.equipment_margin_amount or 0.0)
            line.total_labor_margin = qty * (line.labor_margin_amount or 0.0)

    # ====== METHODES ONCHANGE ======

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Met à jour le prix d'achat quand le produit change"""
        if self.product_id:
            self.purchase_price = self.product_id.standard_price

    # ====== CONTRAINTES ======

    @api.constrains('equipment_margin_percent', 'labor_margin_percent')
    def _check_margins_positive(self):
        """Vérifie que les marges ne sont pas négatives"""
        for line in self:
            if line.equipment_margin_percent < 0:
                raise UserError(_("Le pourcentage marge équipement ne peut pas être négatif."))
            if line.labor_margin_percent < 0:
                raise UserError(_("Le pourcentage main d'oeuvre ne peut pas être négatif."))

    @api.constrains('quantity')
    def _check_quantity_positive(self):
        """Vérifie que la quantité est positive"""
        for line in self:
            if line.quantity <= 0:
                raise UserError(_("La quantité doit être supérieure à 0."))

    # ====== ACTIONS ======

    def action_sync_to_sale_line(self):
        """Synchronise le prix calculé vers la ligne de devis liée"""
        for line in self:
            if not line.sale_line_id:
                raise UserError(_("Aucune ligne de devis liée. Créez d'abord la ligne."))

            # Vérifier l'état de la commande
            if line.order_id.state not in ('draft', 'sent'):
                raise UserError(_(
                    "Impossible de synchroniser : le devis est dans l'état '%s'. "
                    "La synchronisation n'est possible qu'en état Devis ou Devis envoyé."
                ) % dict(line.order_id._fields['state'].selection).get(line.order_id.state))

            # Mettre à jour la ligne de commande
            line.sale_line_id.write({
                'price_unit': line.sale_price_unit,
                'product_uom_qty': line.quantity,
            })

            # Marquer comme synchronisé
            line.write({
                'is_synced': True,
                'last_sync_date': fields.Datetime.now(),
            })

        return True

    def action_create_sale_line(self):
        """Crée une nouvelle ligne dans le devis à partir du calcul"""
        self.ensure_one()

        if self.sale_line_id:
            raise UserError(_("Une ligne de devis est déjà liée à ce calcul."))

        if self.order_id.state not in ('draft', 'sent'):
            raise UserError(_("Impossible de créer une ligne : le devis n'est plus en brouillon."))

        # Créer la ligne de commande
        sale_line = self.env['sale.order.line'].create({
            'order_id': self.order_id.id,
            'product_id': self.product_id.id,
            'name': self.name or self.product_id.display_name,
            'product_uom_qty': self.quantity,
            'product_uom': self.product_uom_id.id,
            'price_unit': self.sale_price_unit,
        })

        # Lier et marquer synchronisé
        self.write({
            'sale_line_id': sale_line.id,
            'is_synced': True,
            'last_sync_date': fields.Datetime.now(),
        })

        return True

    def write(self, vals):
        """Marque comme désynchronisé si les valeurs de calcul changent"""
        sync_fields = ['purchase_price', 'equipment_margin_percent',
                       'labor_margin_percent', 'quantity', 'product_id']

        # Si on modifie un champ de calcul (autre que is_synced), marquer comme désynchronisé
        if any(f in vals for f in sync_fields) and 'is_synced' not in vals:
            vals['is_synced'] = False

        return super().write(vals)
