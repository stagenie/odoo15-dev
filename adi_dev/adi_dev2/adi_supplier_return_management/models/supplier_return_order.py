# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SupplierReturnOrder(models.Model):
    _name = 'supplier.return.order'
    _description = 'Ordre de retour fournisseur'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    # Reference auto-generee
    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau')
    )

    # Fournisseur
    partner_id = fields.Many2one(
        'res.partner',
        string='Fournisseur',
        required=True,
        tracking=True,
        domain="[('supplier_rank', '>', 0)]",
        states={'draft': [('readonly', False)]},
        readonly=True
    )

    # Date du retour
    date = fields.Date(
        string='Date du retour',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        states={'draft': [('readonly', False)]},
        readonly=True
    )

    # Etat du workflow
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('validated', 'Valide'),
        ('refund_created', 'Avoir cree'),
    ], string='Etat', default='draft', tracking=True, required=True)

    # ==========================================
    # Configuration origine (depuis parametres)
    # ==========================================
    origin_mode = fields.Selection([
        ('none', 'Libre'),
        ('flexible', 'Souple'),
        ('strict', 'Strict'),
    ],
        string='Mode origine',
        compute='_compute_origin_mode',
        help="Mode de selection des produits configure dans les parametres"
    )

    # Section Origine (pour mode strict)
    purchase_order_ids = fields.Many2many(
        'purchase.order',
        'supplier_return_order_purchase_rel',
        'return_order_id',
        'purchase_order_id',
        string='Commandes achat',
        domain="[('partner_id', '=', partner_id), ('state', 'in', ['purchase', 'done'])]",
        states={'draft': [('readonly', False)]},
        readonly=True
    )

    picking_ids = fields.Many2many(
        'stock.picking',
        'supplier_return_order_picking_rel',
        'return_order_id',
        'picking_id',
        string='Bons de reception',
        domain="[('purchase_id', 'in', purchase_order_ids), ('state', '=', 'done'), ('picking_type_code', '=', 'incoming')]",
        states={'draft': [('readonly', False)]},
        readonly=True
    )

    # Raison de retour
    reason_id = fields.Many2one(
        'supplier.return.reason',
        string='Raison du retour',
        required=True,
        tracking=True,
        states={'draft': [('readonly', False)]},
        readonly=True
    )

    # ==========================================
    # Entrepot et Emplacement
    # ==========================================
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Entrepot',
        required=True,
        tracking=True,
        default=lambda self: self._default_warehouse_id(),
        states={'draft': [('readonly', False)]},
        readonly=True
    )

    # Emplacement source (d'ou partent les produits)
    source_location_id = fields.Many2one(
        'stock.location',
        string='Emplacement source',
        required=True,
        tracking=True,
        default=lambda self: self._default_source_location_id(),
        domain="[('id', 'in', allowed_location_ids), ('usage', '=', 'internal')]",
        states={'draft': [('readonly', False)]},
        readonly=True,
        help="Emplacement d'ou partent les produits retournes"
    )

    # Emplacements autorises (selon entrepot selectionne)
    allowed_location_ids = fields.Many2many(
        'stock.location',
        compute='_compute_allowed_location_ids',
        string='Emplacements autorises'
    )

    # Lignes de retour
    line_ids = fields.One2many(
        'supplier.return.order.line',
        'return_order_id',
        string='Lignes de retour',
        states={'draft': [('readonly', False)]},
        readonly=True
    )

    # Lien vers l'avoir cree
    refund_id = fields.Many2one(
        'account.move',
        string='Avoir fournisseur',
        readonly=True,
        copy=False
    )

    # Informations complementaires
    notes = fields.Text(string='Notes')

    company_id = fields.Many2one(
        'res.company',
        string='Societe',
        required=True,
        default=lambda self: self.env.company,
        readonly=True
    )

    user_id = fields.Many2one(
        'res.users',
        string='Responsable',
        default=lambda self: self.env.user,
        tracking=True
    )

    # Montant total
    amount_total = fields.Monetary(
        string='Montant total',
        compute='_compute_amount_total',
        store=True,
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id
    )

    # Compteur pour stat button
    refund_count = fields.Integer(
        string='Nombre d\'avoirs',
        compute='_compute_refund_count'
    )

    # Lien vers le picking de retour (sortie de stock)
    return_picking_id = fields.Many2one(
        'stock.picking',
        string='Expedition retour',
        readonly=True,
        copy=False
    )

    picking_count = fields.Integer(
        string='Nombre d\'expeditions',
        compute='_compute_picking_count'
    )

    # Champs pour les vues ameliorees
    line_count = fields.Integer(
        string='Nb lignes',
        compute='_compute_line_count',
        store=True,
        help="Nombre de lignes de retour"
    )

    days_since_creation = fields.Integer(
        string='Anciennete (jours)',
        compute='_compute_days_since_creation',
        help="Nombre de jours depuis la creation du retour"
    )

    is_late = fields.Boolean(
        string='En retard',
        compute='_compute_is_late',
        help="Retour en attente depuis plus de 7 jours"
    )

    # ==========================================
    # Methodes par defaut
    # ==========================================

    @api.model
    def _default_warehouse_id(self):
        """Retourne le premier entrepot de la societe"""
        return self.env['stock.warehouse'].search([
            ('company_id', '=', self.env.company.id)
        ], limit=1)

    @api.model
    def _default_source_location_id(self):
        """Retourne l'emplacement par defaut (stock principal de l'entrepot)"""
        warehouse = self._default_warehouse_id()
        if warehouse:
            return warehouse.lot_stock_id
        return False

    # ==========================================
    # Methodes compute
    # ==========================================

    @api.depends('line_ids.subtotal')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(order.line_ids.mapped('subtotal'))

    @api.depends('refund_id')
    def _compute_refund_count(self):
        for order in self:
            order.refund_count = 1 if order.refund_id else 0

    @api.depends('return_picking_id')
    def _compute_picking_count(self):
        for order in self:
            order.picking_count = 1 if order.return_picking_id else 0

    @api.depends('line_ids')
    def _compute_line_count(self):
        for order in self:
            order.line_count = len(order.line_ids)

    def _compute_days_since_creation(self):
        """Calcule le nombre de jours depuis la date du retour"""
        today = fields.Date.context_today(self)
        for order in self:
            if order.date:
                delta = today - order.date
                order.days_since_creation = delta.days
            else:
                order.days_since_creation = 0

    def _compute_is_late(self):
        """
        Determine si le retour est en retard:
        - Plus de 7 jours en brouillon
        - Plus de 3 jours en valide sans avoir
        """
        for order in self:
            if order.state == 'draft' and order.days_since_creation > 7:
                order.is_late = True
            elif order.state == 'validated' and not order.refund_id and order.days_since_creation > 3:
                order.is_late = True
            else:
                order.is_late = False

    def _compute_origin_mode(self):
        """Recupere le mode d'origine depuis la configuration"""
        config_param = self.env['ir.config_parameter'].sudo()
        origin_mode = config_param.get_param(
            'adi_supplier_return_management.return_origin_mode', 'none'
        )
        for record in self:
            record.origin_mode = origin_mode

    @api.depends('warehouse_id')
    def _compute_allowed_location_ids(self):
        """Recupere les emplacements internes de l'entrepot selectionne"""
        for record in self:
            if record.warehouse_id:
                locations = self.env['stock.location'].search([
                    ('usage', '=', 'internal'),
                    ('id', 'child_of', record.warehouse_id.view_location_id.id),
                ])
                record.allowed_location_ids = locations
            else:
                record.allowed_location_ids = self.env['stock.location']

    # ==========================================
    # Methodes onchange
    # ==========================================

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Reinitialise les commandes et BR quand le fournisseur change"""
        self.purchase_order_ids = False
        self.picking_ids = False
        self.line_ids = [(5, 0, 0)]

    @api.onchange('purchase_order_ids')
    def _onchange_purchase_order_ids(self):
        """Met a jour les BR disponibles et retire ceux non lies"""
        if self.purchase_order_ids:
            valid_pickings = self.picking_ids.filtered(
                lambda p: p.purchase_id in self.purchase_order_ids
            )
            self.picking_ids = valid_pickings
        else:
            self.picking_ids = False

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        """Reinitialise l'emplacement quand l'entrepot change"""
        self.source_location_id = False
        if self.warehouse_id:
            self.source_location_id = self.warehouse_id.lot_stock_id

    # ==========================================
    # Methodes CRUD
    # ==========================================

    @api.model_create_multi
    def create(self, vals_list):
        """Genere la reference automatiquement"""
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'supplier.return.order'
                ) or _('Nouveau')
        return super().create(vals_list)

    # ==========================================
    # Actions du workflow
    # ==========================================

    def action_validate(self):
        """Valide l'ordre de retour et cree la sortie de stock"""
        for order in self:
            if order.state != 'draft':
                raise UserError(_("Seuls les ordres en brouillon peuvent etre valides."))
            if not order.line_ids:
                raise UserError(_("Ajoutez au moins une ligne de retour."))

            # Verifier les quantites
            for line in order.line_ids:
                if line.qty_returned <= 0:
                    raise UserError(_(
                        "La quantite retournee pour '%s' doit etre positive."
                    ) % line.product_id.display_name)

            # Verifier l'origine si mode strict
            if order.origin_mode == 'strict' and not order.picking_ids:
                raise UserError(_(
                    "L'origine est obligatoire en mode strict. "
                    "Veuillez selectionner au moins un bon de reception."
                ))

            # Creer le picking de retour (sortie de stock vers fournisseur)
            picking = order._create_return_picking()
            order.return_picking_id = picking.id

            order.state = 'validated'
            order.message_post(body=_("Ordre de retour valide par %s. Expedition %s creee.") % (
                self.env.user.name, picking.name
            ))

    def _create_return_picking(self):
        """Cree le picking de retour (sortie vers fournisseur)"""
        self.ensure_one()

        # Type d'operation: SORTIE (expedition)
        picking_type = self.warehouse_id.out_type_id

        # Emplacement destination: fournisseurs
        supplier_location = self.env.ref('stock.stock_location_suppliers')

        # Preparer les mouvements de stock
        move_vals = []
        for line in self.line_ids:
            move_vals.append((0, 0, {
                'name': line.product_id.display_name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.qty_returned,
                'product_uom': line.product_id.uom_id.id,
                'location_id': self.source_location_id.id,
                'location_dest_id': supplier_location.id,
            }))

        # Creer le picking
        picking_vals = {
            'picking_type_id': picking_type.id,
            'partner_id': self.partner_id.id,
            'origin': self.name,
            'location_id': self.source_location_id.id,
            'location_dest_id': supplier_location.id,
            'move_ids_without_package': move_vals,
        }

        picking = self.env['stock.picking'].create(picking_vals)

        # Confirmer et assigner le picking
        picking.action_confirm()
        picking.action_assign()

        return picking

    def action_create_refund(self):
        """Cree l'avoir fournisseur"""
        self.ensure_one()
        if self.state != 'validated':
            raise UserError(_("L'ordre doit etre valide avant de creer l'avoir."))

        if self.refund_id:
            raise UserError(_("Un avoir a deja ete cree pour cet ordre."))

        # Preparer les lignes de l'avoir
        invoice_lines = []
        for line in self.line_ids:
            # Recuperer les taxes d'achat du produit
            taxes = line.product_id.supplier_taxes_id.filtered(
                lambda t: t.company_id == self.company_id
            )

            invoice_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'quantity': line.qty_returned,
                'price_unit': line.price_unit,
                'name': line.product_id.display_name,
                'tax_ids': [(6, 0, taxes.ids)],
            }))

        # Creer l'avoir fournisseur (in_refund)
        refund_vals = {
            'move_type': 'in_refund',
            'partner_id': self.partner_id.id,
            'invoice_date': self.date,
            'invoice_origin': self.name,
            'ref': _("Retour fournisseur %s - %s") % (self.name, self.reason_id.name),
            'supplier_return_order_id': self.id,
            'invoice_line_ids': invoice_lines,
        }

        refund = self.env['account.move'].create(refund_vals)

        self.write({
            'refund_id': refund.id,
            'state': 'refund_created',
        })

        self.message_post(body=_("Avoir fournisseur %s cree") % refund.name)

        # Retourner l'action pour voir l'avoir
        return {
            'type': 'ir.actions.act_window',
            'name': _('Avoir fournisseur'),
            'res_model': 'account.move',
            'res_id': refund.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_picking(self):
        """Ouvre le picking de retour"""
        self.ensure_one()
        if not self.return_picking_id:
            return
        return {
            'type': 'ir.actions.act_window',
            'name': _('Expedition retour'),
            'res_model': 'stock.picking',
            'res_id': self.return_picking_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_refund(self):
        """Ouvre l'avoir lie"""
        self.ensure_one()
        if not self.refund_id:
            return
        return {
            'type': 'ir.actions.act_window',
            'name': _('Avoir fournisseur'),
            'res_model': 'account.move',
            'res_id': self.refund_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_draft(self):
        """Remet en brouillon (si pas d'avoir ni de picking)"""
        for order in self:
            if order.refund_id:
                raise UserError(_(
                    "Impossible de remettre en brouillon un ordre avec avoir."
                ))
            if order.return_picking_id:
                raise UserError(_(
                    "Impossible de remettre en brouillon un ordre avec expedition."
                ))
            order.state = 'draft'
            order.message_post(body=_("Ordre remis en brouillon par %s") % self.env.user.name)
