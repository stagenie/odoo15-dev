# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProjectCostingWizard(models.TransientModel):
    _name = 'project.costing.wizard'
    _description = 'Wizard de saisie costing projet'

    # ====== CHAMPS PRINCIPAUX ======
    order_id = fields.Many2one(
        'sale.order',
        string='Devis',
        required=True,
        readonly=True,
        default=lambda self: self.env.context.get('default_order_id')
    )

    order_state = fields.Selection(
        related='order_id.state',
        readonly=True
    )

    currency_id = fields.Many2one(
        related='order_id.currency_id',
        readonly=True
    )

    # ====== LIGNES DU WIZARD ======
    line_ids = fields.One2many(
        'project.costing.wizard.line',
        'wizard_id',
        string='Lignes de calcul'
    )

    # ====== OPTIONS ======
    auto_create_sale_lines = fields.Boolean(
        string='Créer automatiquement les lignes de devis',
        default=True,
        help="Si coché, crée les lignes dans le devis après validation"
    )

    # ====== MARGES PAR DEFAUT ======
    default_equipment_margin = fields.Float(
        string='% Équipement par défaut',
        default=0.0
    )

    default_labor_margin = fields.Float(
        string='% M.O. par défaut',
        default=0.0
    )

    # ====== TOTAUX ======
    total_cost = fields.Monetary(
        string='Total Coût',
        compute='_compute_totals',
        currency_field='currency_id'
    )

    total_sale = fields.Monetary(
        string='Total Vente',
        compute='_compute_totals',
        currency_field='currency_id'
    )

    total_margin = fields.Monetary(
        string='Marge Totale',
        compute='_compute_totals',
        currency_field='currency_id'
    )

    total_equipment_margin = fields.Monetary(
        string='Total Marge Équipement',
        compute='_compute_totals',
        currency_field='currency_id'
    )

    total_labor_margin = fields.Monetary(
        string="Total Main d'Oeuvre",
        compute='_compute_totals',
        currency_field='currency_id'
    )

    # ====== SOUS-TRAITANCE ======
    subcontracting_percent = fields.Float(
        string='% Sous-traitance',
        digits=(16, 2),
        default=0.0,
    )

    subcontracting_amount = fields.Monetary(
        string='Montant Sous-traitance',
        compute='_compute_totals',
        currency_field='currency_id'
    )

    total_margin_net = fields.Monetary(
        string='Marge Nette',
        compute='_compute_totals',
        currency_field='currency_id'
    )

    margin_percent = fields.Float(
        string='% Marge',
        compute='_compute_totals',
        digits=(16, 2)
    )

    # ====== METHODES COMPUTE ======

    @api.depends(
        'line_ids.subtotal_cost',
        'line_ids.subtotal_sale',
        'line_ids.total_equipment_margin',
        'line_ids.total_labor_margin',
        'subcontracting_percent',
    )
    def _compute_totals(self):
        for wizard in self:
            wizard.total_cost = sum(wizard.line_ids.mapped('subtotal_cost'))
            wizard.total_sale = sum(wizard.line_ids.mapped('subtotal_sale'))
            wizard.total_margin = wizard.total_sale - wizard.total_cost
            wizard.total_equipment_margin = sum(wizard.line_ids.mapped('total_equipment_margin'))
            wizard.total_labor_margin = sum(wizard.line_ids.mapped('total_labor_margin'))

            # Sous-traitance
            wizard.subcontracting_amount = (
                wizard.total_labor_margin * (wizard.subcontracting_percent or 0.0) / 100.0
            )
            wizard.total_margin_net = wizard.total_margin - wizard.subcontracting_amount
            if wizard.total_cost > 0:
                wizard.margin_percent = (wizard.total_margin_net / wizard.total_cost) * 100
            else:
                wizard.margin_percent = 0.0

    # ====== ACTIONS ======

    def action_apply_default_margins(self):
        """Applique les marges par défaut à toutes les lignes"""
        for line in self.line_ids:
            line.equipment_margin_percent = self.default_equipment_margin
            line.labor_margin_percent = self.default_labor_margin

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.costing.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_add_from_sale_lines(self):
        """Importe les lignes existantes du devis"""
        self.ensure_one()

        existing_products = self.line_ids.mapped('product_id')

        for sale_line in self.order_id.order_line:
            if sale_line.product_id and sale_line.product_id not in existing_products:
                # Ne pas importer les lignes de type "section" ou "note"
                if sale_line.display_type:
                    continue

                self.env['project.costing.wizard.line'].create({
                    'wizard_id': self.id,
                    'product_id': sale_line.product_id.id,
                    'quantity': sale_line.product_uom_qty,
                    'sale_line_id': sale_line.id,
                    'equipment_margin_percent': self.default_equipment_margin,
                    'labor_margin_percent': self.default_labor_margin,
                })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.costing.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_confirm(self):
        """Valide et crée les lignes de costing"""
        self.ensure_one()

        if not self.line_ids:
            raise UserError(_("Ajoutez au moins une ligne de calcul."))

        if self.order_id.state not in ('draft', 'sent'):
            raise UserError(_("Le devis doit être en état brouillon ou envoyé."))

        # Reporter le % sous-traitance sur le devis
        if self.subcontracting_percent:
            self.order_id.costing_subcontracting_percent = self.subcontracting_percent

        created_lines = self.env['project.costing.line']

        for wiz_line in self.line_ids:
            costing_line = self.env['project.costing.line'].create({
                'order_id': self.order_id.id,
                'product_id': wiz_line.product_id.id,
                'quantity': wiz_line.quantity,
                'purchase_price': wiz_line.purchase_price,
                'equipment_margin_percent': wiz_line.equipment_margin_percent,
                'labor_margin_percent': wiz_line.labor_margin_percent,
                'sale_line_id': wiz_line.sale_line_id.id if wiz_line.sale_line_id else False,
            })
            created_lines |= costing_line

            # Synchronisation automatique si demandé
            if self.auto_create_sale_lines:
                if wiz_line.sale_line_id:
                    costing_line.action_sync_to_sale_line()
                else:
                    costing_line.action_create_sale_line()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Costing créé'),
                'message': _('%d ligne(s) de calcul créée(s)') % len(created_lines),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }


class ProjectCostingWizardLine(models.TransientModel):
    _name = 'project.costing.wizard.line'
    _description = 'Ligne wizard costing'

    # ====== RELATIONS ======
    wizard_id = fields.Many2one(
        'project.costing.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )

    product_id = fields.Many2one(
        'product.product',
        string='Produit',
        required=True,
        domain="[('sale_ok', '=', True)]"
    )

    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Ligne devis existante'
    )

    # ====== QUANTITE ET PRIX ======
    quantity = fields.Float(
        string='Quantité',
        required=True,
        default=1.0,
        digits='Product Unit of Measure'
    )

    purchase_price = fields.Float(
        string="Prix d'achat",
        digits='Product Price',
        compute='_compute_purchase_price',
        store=True,
        readonly=False
    )

    # ====== MARGES ======
    equipment_margin_percent = fields.Float(
        string='% Équipement',
        default=0.0
    )

    labor_margin_percent = fields.Float(
        string='% M.O.',
        default=0.0
    )

    # ====== CALCULS ======
    sale_price_unit = fields.Float(
        string='Prix Vente Unit.',
        compute='_compute_sale_price',
        store=True,
        digits='Product Price'
    )

    equipment_margin_amount = fields.Float(
        string='Montant Marge Équipement',
        compute='_compute_sale_price',
        store=True,
        digits='Product Price'
    )

    labor_margin_amount = fields.Float(
        string="Montant Main d'Oeuvre",
        compute='_compute_sale_price',
        store=True,
        digits='Product Price'
    )

    subtotal_cost = fields.Float(
        string='Sous-total Coût',
        compute='_compute_subtotals',
        store=True
    )

    subtotal_sale = fields.Float(
        string='Sous-total Vente',
        compute='_compute_subtotals',
        store=True
    )

    total_equipment_margin = fields.Float(
        string='Total Marge Équipement',
        compute='_compute_subtotals',
        store=True
    )

    total_labor_margin = fields.Float(
        string="Total Main d'Oeuvre",
        compute='_compute_subtotals',
        store=True
    )

    currency_id = fields.Many2one(
        related='wizard_id.currency_id'
    )

    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unité',
        related='product_id.uom_id',
        readonly=True
    )

    # ====== METHODES COMPUTE ======

    @api.depends('product_id')
    def _compute_purchase_price(self):
        for line in self:
            if line.product_id:
                line.purchase_price = line.product_id.standard_price
            else:
                line.purchase_price = 0.0

    @api.depends('purchase_price', 'equipment_margin_percent', 'labor_margin_percent')
    def _compute_sale_price(self):
        for line in self:
            cost = line.purchase_price or 0.0
            eq_pct = (line.equipment_margin_percent or 0.0) / 100.0
            labor_pct = (line.labor_margin_percent or 0.0) / 100.0
            line.equipment_margin_amount = cost * eq_pct
            line.labor_margin_amount = cost * labor_pct
            line.sale_price_unit = cost * (1 + eq_pct + labor_pct)

    @api.depends('quantity', 'purchase_price', 'sale_price_unit',
                 'equipment_margin_amount', 'labor_margin_amount')
    def _compute_subtotals(self):
        for line in self:
            qty = line.quantity or 0.0
            line.subtotal_cost = qty * (line.purchase_price or 0.0)
            line.subtotal_sale = qty * (line.sale_price_unit or 0.0)
            line.total_equipment_margin = qty * (line.equipment_margin_amount or 0.0)
            line.total_labor_margin = qty * (line.labor_margin_amount or 0.0)

    # ====== METHODES ONCHANGE ======

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.purchase_price = self.product_id.standard_price
