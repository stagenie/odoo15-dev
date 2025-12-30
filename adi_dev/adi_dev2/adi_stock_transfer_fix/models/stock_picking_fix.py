# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StockPickingFix(models.Model):
    """
    Modèle pour identifier et corriger les pickings Odoo bloqués.

    Un picking est considéré "bloqué" si:
    - État = 'assigned' ou 'confirmed' ou 'waiting'
    - Et au moins un mouvement a un stock source insuffisant
    """
    _name = 'adi.stock.picking.fix'
    _description = 'Diagnostic et Correction des Pickings Bloqués'
    _order = 'picking_id desc'
    _rec_name = 'picking_name'

    # === Champs de référence ===
    picking_id = fields.Many2one(
        'stock.picking',
        string='Picking',
        required=True,
        ondelete='cascade',
        index=True
    )
    picking_name = fields.Char(
        related='picking_id.name',
        string='Référence',
        store=True
    )
    picking_state = fields.Selection(
        related='picking_id.state',
        string='État Picking',
        store=True
    )
    picking_type_id = fields.Many2one(
        related='picking_id.picking_type_id',
        string='Type d\'opération'
    )

    # === Emplacements ===
    location_id = fields.Many2one(
        related='picking_id.location_id',
        string='Emplacement Source'
    )
    location_dest_id = fields.Many2one(
        related='picking_id.location_dest_id',
        string='Emplacement Destination'
    )

    # === Lien avec transfert (si applicable) ===
    transfer_id = fields.Many2one(
        related='picking_id.transfer_id',
        string='Transfert Associé'
    )

    # === Diagnostic ===
    issue_type = fields.Selection([
        ('stock_insufficient', 'Stock source insuffisant'),
        ('stock_negative', 'Stock source négatif'),
        ('reservation_issue', 'Problème de réservation'),
        ('other', 'Autre problème'),
    ], string='Type de Problème', compute='_compute_diagnosis', store=True)

    diagnosis = fields.Text(
        string='Diagnostic',
        compute='_compute_diagnosis',
        store=True
    )

    can_fix = fields.Boolean(
        string='Correction Possible',
        compute='_compute_diagnosis',
        store=True
    )

    fix_action = fields.Text(
        string='Action de Correction',
        compute='_compute_diagnosis',
        store=True
    )

    # === Lignes bloquées ===
    blocked_line_ids = fields.One2many(
        'adi.stock.picking.fix.line',
        'fix_id',
        string='Lignes Bloquées'
    )
    blocked_line_count = fields.Integer(
        compute='_compute_blocked_line_count',
        string='Nb Lignes Bloquées'
    )

    # === État de correction ===
    state = fields.Selection([
        ('detected', 'Détecté'),
        ('analyzed', 'Analysé'),
        ('fixed', 'Corrigé'),
        ('failed', 'Échec'),
    ], string='État', default='detected')

    fix_date = fields.Datetime(string='Date Correction')
    fix_user_id = fields.Many2one('res.users', string='Corrigé par')
    fix_notes = fields.Text(string='Notes de Correction')

    @api.depends('picking_id', 'picking_state')
    def _compute_diagnosis(self):
        """Calcule le diagnostic et les actions possibles"""
        for record in self:
            picking = record.picking_id

            if not picking:
                record.issue_type = False
                record.diagnosis = _("Aucun picking associé")
                record.can_fix = False
                record.fix_action = False
                continue

            issues = []
            fix_actions = []
            can_fix = True
            issue_type = 'other'

            # Analyser chaque mouvement
            has_stock_issue = False
            has_negative_stock = False

            for move in picking.move_lines:
                if move.state in ('done', 'cancel'):
                    continue

                # Vérifier le stock disponible
                quants = self.env['stock.quant']._gather(
                    move.product_id,
                    move.location_id,
                    strict=True
                )
                available_qty = sum(quants.mapped('quantity'))

                if available_qty < 0:
                    has_negative_stock = True
                    issues.append(_("Stock NÉGATIF pour %s dans %s: %.2f") % (
                        move.product_id.display_name,
                        move.location_id.complete_name,
                        available_qty
                    ))
                elif available_qty < move.product_uom_qty:
                    has_stock_issue = True
                    issues.append(_("Stock insuffisant pour %s: %.2f disponible / %.2f demandé") % (
                        move.product_id.display_name,
                        available_qty,
                        move.product_uom_qty
                    ))

            if has_negative_stock:
                issue_type = 'stock_negative'
                fix_actions.append(_("Corriger le stock négatif via ajustement d'inventaire ou correction SQL"))
            elif has_stock_issue:
                issue_type = 'stock_insufficient'
                fix_actions.append(_("Option 1: Ajuster les quantités du picking aux quantités disponibles"))
                fix_actions.append(_("Option 2: Forcer la validation (peut créer du stock négatif)"))
                fix_actions.append(_("Option 3: Attendre un réapprovisionnement"))

            # Construire le diagnostic
            if issues:
                record.diagnosis = '\n'.join(['• ' + i for i in issues])
                record.fix_action = '\n'.join(['→ ' + a for a in fix_actions]) if fix_actions else _("Analyse manuelle requise")
            else:
                record.diagnosis = _("Aucun problème de stock détecté")
                can_fix = False
                record.fix_action = False

            record.issue_type = issue_type
            record.can_fix = can_fix and bool(issues)

    @api.depends('blocked_line_ids')
    def _compute_blocked_line_count(self):
        for record in self:
            record.blocked_line_count = len(record.blocked_line_ids)

    def action_analyze(self):
        """Analyser en détail le picking et créer les lignes bloquées"""
        self.ensure_one()

        # Supprimer les anciennes lignes
        self.blocked_line_ids.unlink()

        picking = self.picking_id
        BlockedLine = self.env['adi.stock.picking.fix.line']

        for move in picking.move_lines:
            if move.state in ('done', 'cancel'):
                continue

            product = move.product_id
            location = move.location_id

            # Stock disponible
            quants = self.env['stock.quant']._gather(product, location, strict=True)
            qty_available = sum(quants.mapped('quantity'))
            qty_reserved = sum(quants.mapped('reserved_quantity'))

            # Quantité dans le move
            qty_demanded = move.product_uom_qty
            qty_reserved_move = sum(move.move_line_ids.mapped('product_uom_qty'))

            # Déterminer si la ligne est bloquée
            is_blocked = qty_available < qty_demanded

            BlockedLine.create({
                'fix_id': self.id,
                'move_id': move.id,
                'product_id': product.id,
                'location_id': location.id,
                'quantity_demanded': qty_demanded,
                'quantity_available': qty_available,
                'quantity_reserved': qty_reserved_move,
                'is_blocked': is_blocked,
                'shortage': qty_demanded - qty_available if is_blocked else 0,
            })

        self.state = 'analyzed'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'adi.stock.picking.fix',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_fix_adjust_quantities(self):
        """Corriger en ajustant les quantités aux disponibilités"""
        self.ensure_one()

        picking = self.picking_id

        if picking.state == 'done':
            raise UserError(_("Le picking est déjà validé."))

        adjustments_made = []

        for move in picking.move_lines:
            if move.state in ('done', 'cancel'):
                continue

            # Stock disponible
            quants = self.env['stock.quant']._gather(
                move.product_id, move.location_id, strict=True
            )
            qty_available = sum(quants.mapped('quantity'))

            if qty_available < move.product_uom_qty and qty_available > 0:
                old_qty = move.product_uom_qty
                move.product_uom_qty = qty_available
                # Mettre à jour les move_lines aussi
                for ml in move.move_line_ids:
                    if ml.product_uom_qty > qty_available:
                        ml.product_uom_qty = qty_available
                        ml.qty_done = qty_available
                adjustments_made.append(
                    _("%s: %.2f → %.2f") % (move.product_id.default_code or move.product_id.name, old_qty, qty_available)
                )
            elif qty_available <= 0:
                adjustments_made.append(
                    _("%s: Annulé (stock %.2f)") % (move.product_id.default_code or move.product_id.name, qty_available)
                )
                move._action_cancel()

        self.write({
            'state': 'fixed',
            'fix_date': fields.Datetime.now(),
            'fix_user_id': self.env.user.id,
            'fix_notes': _("Quantités ajustées:\n%s") % '\n'.join(adjustments_made) if adjustments_made else _("Aucun ajustement nécessaire"),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Correction effectuée'),
                'message': _('Les quantités ont été ajustées. Vous pouvez maintenant valider le picking.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_fix_force_validate(self):
        """Forcer la validation du picking (peut créer du stock négatif)"""
        self.ensure_one()

        picking = self.picking_id

        if picking.state == 'done':
            raise UserError(_("Le picking est déjà validé."))

        try:
            # Mettre les qty_done égales aux qty demandées
            for move in picking.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                for ml in move.move_line_ids:
                    ml.qty_done = ml.product_uom_qty
                if not move.move_line_ids:
                    move.quantity_done = move.product_uom_qty

            # Valider avec skip_backorder
            picking.with_context(skip_backorder=True).button_validate()

            self.write({
                'state': 'fixed',
                'fix_date': fields.Datetime.now(),
                'fix_user_id': self.env.user.id,
                'fix_notes': _("Validation forcée avec skip_backorder=True"),
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Picking validé'),
                    'message': _('Le picking a été forcé. Attention: cela peut avoir créé du stock négatif.'),
                    'type': 'warning',
                    'sticky': True,
                }
            }
        except Exception as e:
            self.write({
                'state': 'failed',
                'fix_notes': _("Erreur: %s") % str(e),
            })
            raise UserError(_("Erreur lors de la validation forcée:\n%s") % str(e))

    def action_fix_stock_negative(self):
        """Corriger les stocks négatifs dans l'emplacement source"""
        self.ensure_one()

        picking = self.picking_id
        corrections_made = []

        for move in picking.move_lines:
            if move.state in ('done', 'cancel'):
                continue

            quants = self.env['stock.quant']._gather(
                move.product_id, move.location_id, strict=True
            )
            current_qty = sum(quants.mapped('quantity'))

            if current_qty < 0:
                # Corriger le stock négatif en le mettant à la quantité demandée
                target_qty = move.product_uom_qty
                for quant in quants:
                    if quant.quantity < 0:
                        adjustment = target_qty - quant.quantity
                        quant.sudo().write({'quantity': target_qty})
                        corrections_made.append(
                            _("%s dans %s: %.2f → %.2f") % (
                                move.product_id.default_code or move.product_id.name,
                                move.location_id.name,
                                current_qty,
                                target_qty
                            )
                        )
                        break

        if corrections_made:
            self.write({
                'state': 'fixed',
                'fix_date': fields.Datetime.now(),
                'fix_user_id': self.env.user.id,
                'fix_notes': _("Stocks négatifs corrigés:\n%s") % '\n'.join(corrections_made),
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Stocks corrigés'),
                    'message': _('%d stock(s) négatif(s) corrigé(s).') % len(corrections_made),
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            raise UserError(_("Aucun stock négatif à corriger."))

    def action_view_picking(self):
        """Voir le picking original"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': self.picking_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def action_detect_blocked_pickings(self):
        """
        Détecte tous les pickings bloqués et crée les enregistrements de diagnostic.
        """
        # Chercher les pickings en attente avec problème de stock potentiel
        pickings_to_check = self.env['stock.picking'].search([
            ('state', 'in', ['assigned', 'confirmed', 'waiting']),
            ('picking_type_id.code', 'in', ['internal', 'outgoing']),  # Transferts internes et sorties
        ])

        blocked_pickings = self.env['stock.picking']

        for picking in pickings_to_check:
            # Vérifier si au moins un produit a un stock insuffisant
            for move in picking.move_lines:
                if move.state in ('done', 'cancel'):
                    continue

                quants = self.env['stock.quant']._gather(
                    move.product_id,
                    move.location_id,
                    strict=True
                )
                available_qty = sum(quants.mapped('quantity'))

                if available_qty < move.product_uom_qty:
                    blocked_pickings |= picking
                    break  # Un seul produit suffit pour marquer le picking comme bloqué

        # Créer ou mettre à jour les enregistrements de diagnostic
        existing_fix_ids = self.search([]).mapped('picking_id.id')
        created_count = 0

        for picking in blocked_pickings:
            if picking.id not in existing_fix_ids:
                self.create({
                    'picking_id': picking.id,
                    'state': 'detected',
                })
                created_count += 1

        # Supprimer les anciens enregistrements qui ne sont plus bloqués
        obsolete = self.search([
            ('picking_id', 'not in', blocked_pickings.ids),
            ('state', '!=', 'fixed'),
        ])
        obsolete.unlink()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Détection terminée'),
                'message': _('%d picking(s) bloqué(s) détecté(s). %d nouveau(x).') % (
                    len(blocked_pickings), created_count
                ),
                'type': 'success',
                'sticky': False,
            }
        }


class StockPickingFixLine(models.Model):
    """Détail des lignes bloquées d'un picking"""
    _name = 'adi.stock.picking.fix.line'
    _description = 'Ligne de Diagnostic Picking'
    _order = 'is_blocked desc, product_id'

    fix_id = fields.Many2one(
        'adi.stock.picking.fix',
        string='Diagnostic',
        required=True,
        ondelete='cascade'
    )
    move_id = fields.Many2one(
        'stock.move',
        string='Mouvement',
        required=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Produit',
        required=True
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Emplacement Source'
    )
    quantity_demanded = fields.Float(
        string='Qté Demandée',
        digits='Product Unit of Measure'
    )
    quantity_available = fields.Float(
        string='Qté Disponible',
        digits='Product Unit of Measure'
    )
    quantity_reserved = fields.Float(
        string='Qté Réservée',
        digits='Product Unit of Measure'
    )
    shortage = fields.Float(
        string='Manque',
        digits='Product Unit of Measure'
    )
    is_blocked = fields.Boolean(
        string='Bloqué'
    )
