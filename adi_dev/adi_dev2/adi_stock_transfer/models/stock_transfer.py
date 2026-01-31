# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class StockTransfer(models.Model):
    _name = 'adi.stock.transfer'
    _description = 'Transfert de Stock Inter-Dépôts'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        'Référence',
        required=True,
        readonly=True,
        default='Nouveau',
        copy=False,
        tracking=True
    )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('requested', 'Demandé'),
        ('approved', 'Approuvé'),
        ('in_transit', 'En Transit'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé')
    ], string='État', default='draft', tracking=True, index=True)

    # Champ pour identifier si c'est un transfert inter-sociétés
    is_inter_company = fields.Boolean(
        'Transfert Inter-Sociétés',
        compute='_compute_is_inter_company',
        store=True
    )

    # Informations de base
    request_date = fields.Datetime(
        'Date de Demande',
        default=fields.Datetime.now,
        tracking=True,
        required=True
    )

    scheduled_date = fields.Datetime(
        'Date Prévue',
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )

    # Utilisateurs
    requester_id = fields.Many2one(
        'res.users',
        'Demandeur',
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    validator_id = fields.Many2one(
        'res.users',
        'Validateur',
        tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)], 'requested': [('readonly', False)]}
    )

    # Configuration Multi-Sociétés
    source_company_id = fields.Many2one(
        'res.company',
        'Société Source',
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    dest_company_id = fields.Many2one(
        'res.company',
        'Société Destination',
        required=True,
        tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    # Entrepôts
    source_warehouse_id = fields.Many2one(
        'stock.warehouse',
        'Entrepôt Source',
        required=True,
        tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    dest_warehouse_id = fields.Many2one(
        'stock.warehouse',
        'Entrepôt Destination',
        required=True,
        tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    # Emplacements
    source_location_id = fields.Many2one(
        'stock.location',
        'Emplacement Source',
        required=True,
        tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    dest_location_id = fields.Many2one(
        'stock.location',
        'Emplacement Destination',
        required=True,
        tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    # Emplacement Transit pour le suivi des marchandises en cours de transfert
    transit_location_id = fields.Many2one(
        'stock.location',
        'Emplacement Transit',
        readonly=True,
        help="Emplacement intermédiaire pour suivre les marchandises en transit"
    )

    # Lignes de transfert
    transfer_line_ids = fields.One2many(
        'adi.stock.transfer.line',
        'transfer_id',
        'Lignes de Transfert',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'requested': [('readonly', False)],
            'approved': [('readonly', False)],
            'in_transit': [('readonly', False)]
        }
    )

    # Mouvements de stock générés
    source_picking_id = fields.Many2one(
        'stock.picking',
        'Bon de Sortie',
        readonly=True
    )

    dest_picking_id = fields.Many2one(
        'stock.picking',
        'Bon d\'Entrée',
        readonly=True
    )

    picking_ids = fields.One2many(
        'stock.picking',
        'transfer_id',
        'Bons de Transfert',
        readonly=True
    )

    picking_count = fields.Integer(
        'Nombre de Transferts',
        compute='_compute_picking_count'
    )

    # Notes et commentaires
    note = fields.Text('Notes Internes')
    rejection_reason = fields.Text('Raison du Rejet', tracking=True)

    # Totaux quantités
    total_qty_sent = fields.Float(
        'Total Envoyé',
        compute='_compute_qty_totals',
        store=True
    )

    total_qty_received = fields.Float(
        'Total Reçu',
        compute='_compute_qty_totals',
        store=True
    )

    # Champs calculés
    total_products = fields.Integer(
        'Nombre de Produits',
        compute='_compute_totals',
        store=True
    )

    total_quantity = fields.Float(
        'Quantité Totale',
        compute='_compute_totals',
        store=True
    )

    # Mode mono-société
    is_single_company_mode = fields.Boolean(
        'Mode Mono-Société',
        compute='_compute_single_company_mode'
    )

    @api.depends('source_company_id', 'dest_company_id')
    def _compute_is_inter_company(self):
        """Détermine si c'est un transfert inter-sociétés"""
        for record in self:
            record.is_inter_company = record.source_company_id != record.dest_company_id

    @api.depends('transfer_line_ids', 'transfer_line_ids.quantity')
    def _compute_totals(self):
        """Calcul des totaux du transfert"""
        for record in self:
            record.total_products = len(record.transfer_line_ids)
            record.total_quantity = sum(record.transfer_line_ids.mapped('quantity'))

    @api.depends('picking_ids')
    def _compute_picking_count(self):
        """Compte le nombre de bons de transfert"""
        for record in self:
            record.picking_count = len(record.picking_ids)

    @api.depends('transfer_line_ids.qty_sent', 'transfer_line_ids.qty_received')
    def _compute_qty_totals(self):
        """Calcul des totaux de quantités"""
        for record in self:
            record.total_qty_sent = sum(record.transfer_line_ids.mapped('qty_sent'))
            record.total_qty_received = sum(record.transfer_line_ids.mapped('qty_received'))

    def _compute_single_company_mode(self):
        """Détermine si on est en mode mono-société"""
        company_count = self.env['res.company'].search_count([])
        for record in self:
            record.is_single_company_mode = (company_count == 1)

    def _get_or_create_transit_location(self):
        """Obtenir ou créer l'emplacement transit pour le transfert"""
        self.ensure_one()

        # Chercher d'abord un emplacement transit existant (inter-entrepôts)
        transit_location = self.env.ref('stock.stock_location_inter_wh', raise_if_not_found=False)

        if not transit_location:
            transit_location = self.env['stock.location'].search([
                ('usage', '=', 'transit'),
                '|',
                ('company_id', '=', False),
                ('company_id', '=', self.source_company_id.id)
            ], limit=1)

        if not transit_location:
            parent_location = self.env.ref('stock.stock_location_locations', raise_if_not_found=False)
            transit_location = self.env['stock.location'].sudo().create({
                'name': 'Transit Inter-Dépôts',
                'usage': 'transit',
                'location_id': parent_location.id if parent_location else False,
                'company_id': False,
            })

        return transit_location

    @api.model
    def create(self, vals):
        """Génération automatique du numéro de séquence"""
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('adi.stock.transfer') or 'Nouveau'
        return super(StockTransfer, self).create(vals)

    @api.constrains('source_location_id', 'dest_location_id')
    def _check_locations(self):
        """Vérification que les emplacements sont différents"""
        for record in self:
            if record.source_location_id == record.dest_location_id:
                raise ValidationError(_("L'emplacement source et destination doivent être différents!"))

    @api.onchange('source_company_id')
    def _onchange_source_company(self):
        """Réinitialiser l'entrepôt et l'emplacement source lors du changement de société"""
        self.source_warehouse_id = False
        self.source_location_id = False
        return {
            'domain': {
                'source_warehouse_id': [('company_id', '=', self.source_company_id.id)]
            }
        }

    @api.onchange('dest_company_id')
    def _onchange_dest_company(self):
        """Réinitialiser l'entrepôt et l'emplacement destination lors du changement de société"""
        self.dest_warehouse_id = False
        self.dest_location_id = False
        return {
            'domain': {
                'dest_warehouse_id': [('company_id', '=', self.dest_company_id.id)]
            }
        }

    @api.onchange('source_warehouse_id')
    def _onchange_source_warehouse(self):
        """Réinitialiser l'emplacement source et mettre à jour le domaine"""
        self.source_location_id = False
        if self.source_warehouse_id:
            warehouse_location = self.source_warehouse_id.lot_stock_id
            return {
                'domain': {
                    'source_location_id': [
                        ('usage', '=', 'internal'),
                        ('company_id', '=', self.source_company_id.id),
                        ('id', 'child_of', warehouse_location.id if warehouse_location else False)
                    ]
                }
            }

    @api.onchange('dest_warehouse_id')
    def _onchange_dest_warehouse(self):
        """Réinitialiser l'emplacement destination et mettre à jour le domaine"""
        self.dest_location_id = False
        if self.dest_warehouse_id:
            warehouse_location = self.dest_warehouse_id.lot_stock_id
            return {
                'domain': {
                    'dest_location_id': [
                        ('usage', '=', 'internal'),
                        ('company_id', '=', self.dest_company_id.id),
                        ('id', 'child_of', warehouse_location.id if warehouse_location else False)
                    ]
                }
            }

    @api.model
    def default_get(self, fields_list):
        """Définir les valeurs par défaut"""
        res = super(StockTransfer, self).default_get(fields_list)
        companies = self.env['res.company'].search([])
        if len(companies) == 1:
            res['source_company_id'] = companies.id
            res['dest_company_id'] = companies.id
        return res

    # ================== ACTIONS DU WORKFLOW ==================

    def action_request(self):
        """Passer l'état à 'Demandé'"""
        for record in self:
            if not record.transfer_line_ids:
                raise UserError(_("Vous devez ajouter au moins une ligne de produit!"))

            for line in record.transfer_line_ids:
                line._check_available_quantity()

            record.state = 'requested'

            if record.validator_id:
                record.message_post(
                    body=_("Demande de transfert soumise pour validation"),
                    partner_ids=[record.validator_id.partner_id.id]
                )

    def action_approve(self):
        """Approuver le transfert et créer les mouvements de stock"""
        self.ensure_one()

        if not self.user_has_groups('adi_stock_transfer.group_stock_transfer_validator'):
            raise UserError(_("Seuls les validateurs peuvent approuver les transferts!"))

        if self.is_inter_company:
            self._create_inter_company_pickings()
        else:
            self._create_single_picking()

        self.write({
            'state': 'approved',
            'validator_id': self.env.user.id
        })

        self.message_post(body=_("Transfert approuvé par %s") % self.env.user.name)

    def _create_single_picking(self):
        """Créer les pickings pour un transfert intra-société avec transit"""
        transit_location = self._get_or_create_transit_location()
        self.transit_location_id = transit_location

        # 1. PICKING DE SORTIE: Source → Transit
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'internal'),
            ('warehouse_id', '=', self.source_warehouse_id.id)
        ], limit=1)

        if not picking_type:
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'internal'),
                ('company_id', '=', self.source_company_id.id)
            ], limit=1)

        source_picking_vals = {
            'picking_type_id': picking_type.id,
            'partner_id': self.requester_id.partner_id.id,
            'location_id': self.source_location_id.id,
            'location_dest_id': transit_location.id,
            'scheduled_date': self.scheduled_date,
            'origin': self.name + ' - Sortie',
            'transfer_id': self.id,
            'company_id': self.source_company_id.id,
        }

        source_picking = self.env['stock.picking'].create(source_picking_vals)

        for line in self.transfer_line_ids:
            move_vals = {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'product_uom': line.product_uom_id.id,
                'picking_id': source_picking.id,
                'location_id': self.source_location_id.id,
                'location_dest_id': transit_location.id,
                'company_id': self.source_company_id.id,
            }
            self.env['stock.move'].create(move_vals)

        source_picking.action_confirm()
        self.source_picking_id = source_picking

        # 2. PICKING D'ENTRÉE: Transit → Destination
        dest_picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'internal'),
            ('warehouse_id', '=', self.dest_warehouse_id.id)
        ], limit=1)

        if not dest_picking_type:
            dest_picking_type = picking_type

        dest_picking_vals = {
            'picking_type_id': dest_picking_type.id,
            'partner_id': self.requester_id.partner_id.id,
            'location_id': transit_location.id,
            'location_dest_id': self.dest_location_id.id,
            'scheduled_date': self.scheduled_date,
            'origin': self.name + ' - Entrée',
            'transfer_id': self.id,
            'company_id': self.dest_company_id.id,
        }

        dest_picking = self.env['stock.picking'].create(dest_picking_vals)

        for line in self.transfer_line_ids:
            move_vals = {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'product_uom': line.product_uom_id.id,
                'picking_id': dest_picking.id,
                'location_id': transit_location.id,
                'location_dest_id': self.dest_location_id.id,
                'company_id': self.dest_company_id.id,
            }
            self.env['stock.move'].create(move_vals)

        dest_picking.action_confirm()
        self.dest_picking_id = dest_picking

    def _create_inter_company_pickings(self):
        """Créer deux pickings pour un transfert inter-sociétés"""
        transit_location = self._get_or_create_transit_location()
        self.transit_location_id = transit_location

        # PICKING DE SORTIE (société source)
        out_picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'outgoing'),
            ('warehouse_id', '=', self.source_warehouse_id.id)
        ], limit=1)

        if not out_picking_type:
            out_picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'internal'),
                ('warehouse_id', '=', self.source_warehouse_id.id)
            ], limit=1)

        out_picking_vals = {
            'picking_type_id': out_picking_type.id,
            'partner_id': self.requester_id.partner_id.id,
            'location_id': self.source_location_id.id,
            'location_dest_id': transit_location.id,
            'scheduled_date': self.scheduled_date,
            'origin': self.name + ' - Sortie',
            'transfer_id': self.id,
            'company_id': self.source_company_id.id,
        }

        source_picking = self.env['stock.picking'].with_company(self.source_company_id).create(out_picking_vals)

        for line in self.transfer_line_ids:
            move_vals = {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'product_uom': line.product_uom_id.id,
                'picking_id': source_picking.id,
                'location_id': self.source_location_id.id,
                'location_dest_id': transit_location.id,
                'company_id': self.source_company_id.id,
            }
            self.env['stock.move'].with_company(self.source_company_id).create(move_vals)

        source_picking.action_confirm()

        # PICKING D'ENTRÉE (société destination)
        in_picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'),
            ('warehouse_id', '=', self.dest_warehouse_id.id)
        ], limit=1)

        if not in_picking_type:
            in_picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'internal'),
                ('warehouse_id', '=', self.dest_warehouse_id.id)
            ], limit=1)

        in_picking_vals = {
            'picking_type_id': in_picking_type.id,
            'partner_id': self.requester_id.partner_id.id,
            'location_id': transit_location.id,
            'location_dest_id': self.dest_location_id.id,
            'scheduled_date': self.scheduled_date,
            'origin': self.name + ' - Entrée',
            'transfer_id': self.id,
            'company_id': self.dest_company_id.id,
        }

        dest_picking = self.env['stock.picking'].with_company(self.dest_company_id).create(in_picking_vals)

        for line in self.transfer_line_ids:
            move_vals = {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'product_uom': line.product_uom_id.id,
                'picking_id': dest_picking.id,
                'location_id': transit_location.id,
                'location_dest_id': self.dest_location_id.id,
                'company_id': self.dest_company_id.id,
            }
            self.env['stock.move'].with_company(self.dest_company_id).create(move_vals)

        dest_picking.action_confirm()

        self.source_picking_id = source_picking
        self.dest_picking_id = dest_picking

    def action_start_transit(self):
        """Démarrer le transit - L'entrepôt source envoie les produits"""
        self.ensure_one()

        # Mettre à jour les quantités envoyées sur les lignes
        for line in self.transfer_line_ids:
            if line.qty_sent == 0:
                line.qty_sent = line.quantity

        # Valider le picking de sortie
        if self.source_picking_id and self.source_picking_id.state not in ('done', 'cancel'):
            for move in self.source_picking_id.move_lines:
                transfer_line = self.transfer_line_ids.filtered(
                    lambda l: l.product_id.id == move.product_id.id
                )
                if transfer_line:
                    qty_to_set = transfer_line[0].qty_sent
                    # Travailler directement avec les move_lines pour éviter l'erreur
                    # "Cannot set done quantity from stock move" quand il y a plusieurs lignes
                    if move.move_line_ids:
                        for move_line in move.move_line_ids:
                            move_line.qty_done = move_line.product_uom_qty
                    else:
                        move.quantity_done = qty_to_set
            self.source_picking_id.with_context(skip_backorder=True).button_validate()

        self.state = 'in_transit'
        self.message_post(body=_("Produits envoyés - En transit"))

    def action_done(self):
        """Ouvrir le wizard de confirmation avant de terminer"""
        self.ensure_one()
        return {
            'name': _('Confirmation de Réception'),
            'type': 'ir.actions.act_window',
            'res_model': 'adi.stock.transfer.confirm.done.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_transfer_id': self.id,
            }
        }

    def action_done_confirmed(self):
        """Marquer le transfert comme terminé (réception complète)"""
        self.ensure_one()

        # Mettre les quantités reçues = envoyées (réception complète)
        for line in self.transfer_line_ids:
            if line.qty_sent == 0:
                line.qty_sent = line.quantity
            line.qty_received = line.qty_sent

        # Valider le picking d'entrée
        if self.dest_picking_id and self.dest_picking_id.state not in ('done', 'cancel'):
            for move in self.dest_picking_id.move_lines:
                transfer_line = self.transfer_line_ids.filtered(
                    lambda l: l.product_id.id == move.product_id.id
                )
                if transfer_line:
                    # Travailler directement avec les move_lines pour éviter l'erreur
                    # "Cannot set done quantity from stock move" quand il y a plusieurs lignes
                    if move.move_line_ids:
                        for move_line in move.move_line_ids:
                            move_line.qty_done = move_line.product_uom_qty
                    else:
                        move.quantity_done = transfer_line[0].qty_received
            self.dest_picking_id.with_context(skip_backorder=True).button_validate()

        self.state = 'done'
        self.message_post(body=_("Réception complète - Transfert terminé"))

    def action_cancel(self):
        """Annuler le transfert"""
        for record in self:
            for picking in record.picking_ids:
                if picking.state != 'done':
                    picking.action_cancel()

            record.state = 'cancelled'
            record.message_post(body=_("Transfert annulé"))

    def action_draft(self):
        """Remettre en brouillon"""
        for record in self:
            if record.picking_ids:
                raise UserError(_("Impossible de remettre en brouillon un transfert avec des mouvements de stock!"))
            record.state = 'draft'

    def action_view_picking(self):
        """Afficher les bons de transfert associés"""
        self.ensure_one()
        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        pickings = self.picking_ids
        if len(pickings) == 1:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.id
        else:
            action['domain'] = [('id', 'in', pickings.ids)]

        action['context'] = {'default_transfer_id': self.id}
        return action
