# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockTransferFix(models.Model):
    """
    Modèle pour identifier et corriger les transferts bloqués.

    Un transfert est considéré "bloqué" si:
    - État = 'in_transit' mais source_picking.state != 'done'
    - État = 'done' mais l'un des pickings n'est pas 'done'
    """
    _name = 'adi.stock.transfer.fix'
    _description = 'Diagnostic et Correction des Transferts Bloqués'
    _order = 'transfer_id desc'
    _rec_name = 'transfer_name'

    # === Champs de référence ===
    transfer_id = fields.Many2one(
        'adi.stock.transfer',
        string='Transfert',
        required=True,
        ondelete='cascade',
        index=True
    )
    transfer_name = fields.Char(
        related='transfer_id.name',
        string='Référence',
        store=True
    )
    transfer_state = fields.Selection(
        related='transfer_id.state',
        string='État Transfert',
        store=True
    )

    # === Pickings ===
    source_picking_id = fields.Many2one(
        related='transfer_id.source_picking_id',
        string='Picking Sortie'
    )
    source_picking_state = fields.Selection(
        related='transfer_id.source_picking_id.state',
        string='État Picking Sortie',
        store=True
    )
    dest_picking_id = fields.Many2one(
        related='transfer_id.dest_picking_id',
        string='Picking Entrée'
    )
    dest_picking_state = fields.Selection(
        related='transfer_id.dest_picking_id.state',
        string='État Picking Entrée',
        store=True
    )

    # === Diagnostic ===
    issue_type = fields.Selection([
        ('source_not_validated', 'Picking sortie non validé'),
        ('dest_not_validated', 'Picking entrée non validé'),
        ('both_not_validated', 'Les deux pickings non validés'),
        ('transit_stock_issue', 'Problème de stock transit'),
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
        'adi.stock.transfer.fix.line',
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

    @api.depends('transfer_id', 'transfer_state', 'source_picking_state', 'dest_picking_state')
    def _compute_diagnosis(self):
        """Calcule le diagnostic et les actions possibles"""
        for record in self:
            transfer = record.transfer_id

            if not transfer:
                record.issue_type = False
                record.diagnosis = _("Aucun transfert associé")
                record.can_fix = False
                record.fix_action = False
                continue

            issues = []
            fix_actions = []
            can_fix = True
            issue_type = False

            # Vérifier l'état du transfert vs pickings
            if transfer.state == 'in_transit':
                if record.source_picking_state != 'done':
                    issues.append(_("PROBLÈME PRINCIPAL: Le transfert est 'En Transit' mais le picking de sortie (%s) n'est PAS VALIDÉ (état: %s)") % (
                        transfer.source_picking_id.name or 'N/A',
                        record.source_picking_state or 'N/A'
                    ))
                    issues.append(_("CONSÉQUENCE: Le stock n'a jamais été transféré vers l'emplacement transit"))
                    issues.append(_("BLOCAGE: La réception est impossible car le stock transit est à 0"))
                    fix_actions.append(_("1. Valider le picking de sortie (%s) pour transférer le stock vers le transit") % (
                        transfer.source_picking_id.name or 'N/A'
                    ))
                    fix_actions.append(_("2. Après correction, la réception sera possible"))
                    issue_type = 'source_not_validated'

                if record.dest_picking_state not in ('assigned', 'waiting', 'confirmed'):
                    issues.append(_("Le picking d'entrée (%s) est dans un état inattendu: %s") % (
                        transfer.dest_picking_id.name or 'N/A',
                        record.dest_picking_state or 'N/A'
                    ))

            elif transfer.state == 'done':
                if record.source_picking_state != 'done':
                    issues.append(_("Le transfert est 'Terminé' mais le picking de sortie n'est pas 'done'"))
                    fix_actions.append(_("Valider le picking de sortie"))
                    issue_type = 'source_not_validated'
                if record.dest_picking_state != 'done':
                    issues.append(_("Le transfert est 'Terminé' mais le picking d'entrée n'est pas 'done'"))
                    if issue_type == 'source_not_validated':
                        issue_type = 'both_not_validated'
                    else:
                        issue_type = 'dest_not_validated'

            # Construire le diagnostic
            if issues:
                record.diagnosis = '\n'.join(['• ' + i for i in issues])
                record.fix_action = '\n'.join(['→ ' + a for a in fix_actions]) if fix_actions else _("Analyse manuelle requise")
            else:
                record.diagnosis = _("Aucun problème détecté")
                can_fix = False
                record.fix_action = False

            record.issue_type = issue_type
            record.can_fix = can_fix and bool(fix_actions)

    @api.depends('blocked_line_ids')
    def _compute_blocked_line_count(self):
        for record in self:
            record.blocked_line_count = len(record.blocked_line_ids)

    def action_analyze(self):
        """Analyser en détail le transfert et créer les lignes bloquées"""
        self.ensure_one()

        # Supprimer les anciennes lignes
        self.blocked_line_ids.unlink()

        transfer = self.transfer_id
        transit_location = transfer.transit_location_id

        if not transit_location:
            self.fix_notes = _("Emplacement transit non défini sur le transfert")
            self.state = 'analyzed'
            return

        # Analyser chaque ligne du transfert
        BlockedLine = self.env['adi.stock.transfer.fix.line']

        for line in transfer.transfer_line_ids:
            product = line.product_id

            # Stock dans le transit
            quants = self.env['stock.quant']._gather(
                product,
                transit_location,
                strict=True
            )
            qty_in_transit = sum(quants.mapped('quantity'))

            # Stock dans l'emplacement source original
            quants_source = self.env['stock.quant']._gather(
                product,
                transfer.source_location_id,
                strict=True
            )
            qty_in_source = sum(quants_source.mapped('quantity'))

            # Quantités dans le picking de sortie
            source_move = transfer.source_picking_id.move_lines.filtered(
                lambda m: m.product_id.id == product.id
            )
            qty_demanded = source_move.product_uom_qty if source_move else line.quantity
            qty_done_source = sum(source_move.mapped('move_line_ids.qty_done')) if source_move else 0

            # Déterminer si la ligne est bloquée
            is_blocked = qty_in_transit < line.quantity

            BlockedLine.create({
                'fix_id': self.id,
                'product_id': product.id,
                'quantity_requested': line.quantity,
                'quantity_in_source': qty_in_source,
                'quantity_in_transit': qty_in_transit,
                'quantity_done_source_picking': qty_done_source,
                'is_blocked': is_blocked,
                'blocking_reason': self._get_blocking_reason(
                    line.quantity, qty_in_transit, qty_done_source,
                    transfer.source_picking_id.state if transfer.source_picking_id else 'N/A'
                ),
            })

        self.state = 'analyzed'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'adi.stock.transfer.fix',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _get_blocking_reason(self, qty_requested, qty_transit, qty_done, picking_state):
        """Détermine la raison du blocage"""
        reasons = []

        if picking_state != 'done':
            reasons.append(_("Picking sortie non validé (état: %s)") % picking_state)

        if qty_transit < qty_requested:
            reasons.append(_("Stock transit insuffisant: %.2f / %.2f requis") % (qty_transit, qty_requested))

        if qty_done < qty_requested and picking_state != 'done':
            reasons.append(_("Quantité faite dans picking: %.2f / %.2f") % (qty_done, qty_requested))

        return ' | '.join(reasons) if reasons else _("OK")

    def action_fix(self):
        """Ouvrir le wizard de correction"""
        self.ensure_one()

        if not self.can_fix:
            raise UserError(_("Ce transfert ne peut pas être corrigé automatiquement. Vérifiez le diagnostic."))

        return {
            'name': _('Correction du Transfert %s') % self.transfer_name,
            'type': 'ir.actions.act_window',
            'res_model': 'adi.stock.transfer.fix.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_fix_id': self.id,
                'default_transfer_id': self.transfer_id.id,
            },
        }

    def action_view_transfer(self):
        """Voir le transfert original"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'adi.stock.transfer',
            'res_id': self.transfer_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_source_picking(self):
        """Voir le picking de sortie"""
        self.ensure_one()
        if not self.source_picking_id:
            raise UserError(_("Aucun picking de sortie associé"))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': self.source_picking_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def action_detect_blocked_transfers(self):
        """
        Détecte tous les transferts bloqués et crée les enregistrements de diagnostic.
        Appelé depuis le menu ou un bouton.
        """
        # Chercher les transferts avec incohérences
        blocked_transfers = self.env['adi.stock.transfer'].search([
            '|', '|',
            # Cas 1: in_transit mais source picking pas done
            '&', ('state', '=', 'in_transit'), ('source_picking_id.state', '!=', 'done'),
            # Cas 2: done mais source picking pas done
            '&', ('state', '=', 'done'), ('source_picking_id.state', '!=', 'done'),
            # Cas 3: done mais dest picking pas done (ni cancel qui peut être normal)
            '&', '&', ('state', '=', 'done'), ('dest_picking_id.state', '!=', 'done'), ('dest_picking_id.state', '!=', 'cancel'),
        ])

        # Créer ou mettre à jour les enregistrements de diagnostic
        existing_fix_ids = self.search([]).mapped('transfer_id.id')
        created_count = 0

        for transfer in blocked_transfers:
            if transfer.id not in existing_fix_ids:
                self.create({
                    'transfer_id': transfer.id,
                    'state': 'detected',
                })
                created_count += 1

        # Supprimer les anciens enregistrements qui ne sont plus bloqués
        obsolete = self.search([
            ('transfer_id', 'not in', blocked_transfers.ids),
            ('state', '!=', 'fixed'),
        ])
        obsolete.unlink()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Détection terminée'),
                'message': _('%d transfert(s) bloqué(s) détecté(s). %d nouveau(x).') % (
                    len(blocked_transfers), created_count
                ),
                'type': 'success',
                'sticky': False,
            }
        }


class StockTransferFixLine(models.Model):
    """Détail des lignes bloquées d'un transfert"""
    _name = 'adi.stock.transfer.fix.line'
    _description = 'Ligne de Diagnostic Transfert'
    _order = 'is_blocked desc, product_id'

    fix_id = fields.Many2one(
        'adi.stock.transfer.fix',
        string='Diagnostic',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Produit',
        required=True
    )
    quantity_requested = fields.Float(
        string='Qté Demandée',
        digits='Product Unit of Measure'
    )
    quantity_in_source = fields.Float(
        string='Qté Source',
        digits='Product Unit of Measure',
        help="Quantité actuelle dans l'emplacement source original"
    )
    quantity_in_transit = fields.Float(
        string='Qté Transit',
        digits='Product Unit of Measure',
        help="Quantité actuelle dans l'emplacement transit"
    )
    quantity_done_source_picking = fields.Float(
        string='Qté Faite (Picking)',
        digits='Product Unit of Measure',
        help="Quantité marquée comme faite dans le picking de sortie"
    )
    is_blocked = fields.Boolean(
        string='Bloqué',
        help="La ligne est bloquée si le stock transit est insuffisant"
    )
    blocking_reason = fields.Char(string='Raison du Blocage')
