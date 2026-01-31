# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StockTransferFixWizard(models.TransientModel):
    """Wizard pour corriger un transfert bloqué"""
    _name = 'adi.stock.transfer.fix.wizard'
    _description = 'Assistant de Correction Transfert'

    fix_id = fields.Many2one(
        'adi.stock.transfer.fix',
        string='Diagnostic',
        required=True
    )
    transfer_id = fields.Many2one(
        'adi.stock.transfer',
        string='Transfert',
        required=True
    )

    # Informations de diagnostic
    transfer_name = fields.Char(
        related='transfer_id.name',
        string='Référence'
    )
    transfer_state = fields.Selection(
        related='transfer_id.state',
        string='État Transfert'
    )
    source_picking_id = fields.Many2one(
        related='transfer_id.source_picking_id',
        string='Picking Sortie'
    )
    source_picking_state = fields.Selection(
        related='transfer_id.source_picking_id.state',
        string='État Picking'
    )
    diagnosis = fields.Text(
        related='fix_id.diagnosis',
        string='Diagnostic'
    )

    # Options de correction
    fix_method = fields.Selection([
        ('validate_source', 'Valider le picking de sortie'),
        ('cancel_and_recreate', 'Annuler et recréer le picking'),
    ], string='Méthode de Correction', default='validate_source', required=True)

    skip_backorder = fields.Boolean(
        string='Ignorer les reliquats',
        default=True,
        help="Si coché, le picking sera validé sans créer de reliquat pour les quantités manquantes"
    )

    use_done_quantities = fields.Boolean(
        string='Utiliser les quantités déjà saisies',
        default=True,
        help="Si coché, utilise les quantités 'qty_done' déjà présentes dans les move_lines"
    )

    force_full_quantity = fields.Boolean(
        string='Forcer les quantités complètes',
        default=False,
        help="Si coché, remplit automatiquement toutes les quantités demandées comme faites"
    )

    confirmation = fields.Boolean(
        string="Je confirme vouloir corriger ce transfert",
        default=False
    )

    # Prévisualisation
    preview_lines = fields.Text(
        string='Prévisualisation',
        compute='_compute_preview'
    )

    @api.depends('transfer_id', 'fix_method', 'use_done_quantities', 'force_full_quantity')
    def _compute_preview(self):
        """Calcule la prévisualisation des actions"""
        for wizard in self:
            if not wizard.transfer_id or not wizard.source_picking_id:
                wizard.preview_lines = _("Aucun picking à corriger")
                continue

            lines = []
            picking = wizard.source_picking_id

            lines.append(_("=== PRÉVISUALISATION DE LA CORRECTION ===\n"))
            lines.append(_("Picking: %s (État: %s)\n") % (picking.name, picking.state))
            lines.append(_("Méthode: %s\n") % dict(wizard._fields['fix_method'].selection).get(wizard.fix_method))
            lines.append(_("\n--- Mouvements ---"))

            for move in picking.move_lines:
                qty_demand = move.product_uom_qty
                qty_done_current = sum(move.move_line_ids.mapped('qty_done'))

                if wizard.force_full_quantity:
                    qty_after = qty_demand
                elif wizard.use_done_quantities:
                    qty_after = qty_done_current if qty_done_current > 0 else qty_demand
                else:
                    qty_after = qty_demand

                status = "OK" if qty_after >= qty_demand else "PARTIEL"
                lines.append(
                    _("\n[%s] %s: %.2f / %.2f (actuel: %.2f)") % (
                        status,
                        move.product_id.default_code or move.product_id.name[:20],
                        qty_after,
                        qty_demand,
                        qty_done_current
                    )
                )

            if wizard.skip_backorder:
                lines.append(_("\n\n* Les quantités manquantes seront ignorées (pas de reliquat)"))
            else:
                lines.append(_("\n\n* Un reliquat sera créé pour les quantités manquantes"))

            wizard.preview_lines = '\n'.join(lines)

    def action_fix(self):
        """Exécuter la correction"""
        self.ensure_one()

        if not self.confirmation:
            raise UserError(_("Veuillez confirmer la correction en cochant la case de confirmation."))

        transfer = self.transfer_id
        picking = self.source_picking_id

        if not picking:
            raise UserError(_("Aucun picking de sortie à corriger."))

        if picking.state == 'done':
            raise UserError(_("Le picking est déjà validé."))

        if picking.state == 'cancel':
            raise UserError(_("Le picking est annulé. Utilisez la méthode 'Annuler et recréer'."))

        _logger.info("Correction du transfert %s - Picking %s", transfer.name, picking.name)

        try:
            if self.fix_method == 'validate_source':
                self._fix_validate_source(transfer, picking)
            elif self.fix_method == 'cancel_and_recreate':
                self._fix_cancel_and_recreate(transfer, picking)

            # Mettre à jour le diagnostic
            self.fix_id.write({
                'state': 'fixed',
                'fix_date': fields.Datetime.now(),
                'fix_user_id': self.env.user.id,
                'fix_notes': _("Corrigé avec la méthode: %s") % self.fix_method,
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Correction réussie'),
                    'message': _('Le transfert %s a été corrigé avec succès.') % transfer.name,
                    'type': 'success',
                    'sticky': False,
                    'next': {
                        'type': 'ir.actions.act_window_close',
                    },
                }
            }

        except Exception as e:
            _logger.error("Erreur lors de la correction du transfert %s: %s", transfer.name, str(e))
            self.fix_id.write({
                'state': 'failed',
                'fix_notes': _("Erreur: %s") % str(e),
            })
            raise UserError(_("Erreur lors de la correction:\n%s") % str(e))

    def _fix_validate_source(self, transfer, picking):
        """Corriger en validant le picking de sortie"""
        _logger.info("Validation du picking %s avec skip_backorder=%s", picking.name, self.skip_backorder)

        # Préparer les quantités
        for move in picking.move_lines:
            if self.force_full_quantity:
                # Forcer les quantités complètes
                if move.move_line_ids:
                    remaining = move.product_uom_qty
                    for ml in move.move_line_ids:
                        qty = min(ml.product_uom_qty, remaining)
                        ml.qty_done = qty
                        remaining -= qty
                else:
                    # Créer une move_line si nécessaire
                    move.quantity_done = move.product_uom_qty
            elif not self.use_done_quantities:
                # Utiliser les quantités demandées
                if move.move_line_ids:
                    for ml in move.move_line_ids:
                        ml.qty_done = ml.product_uom_qty
                else:
                    move.quantity_done = move.product_uom_qty

            # Si use_done_quantities, on garde les quantités déjà saisies

        # Valider le picking
        ctx = dict(self.env.context)
        if self.skip_backorder:
            ctx['skip_backorder'] = True

        picking.with_context(**ctx).button_validate()

        _logger.info("Picking %s validé avec succès (état: %s)", picking.name, picking.state)

    def _fix_cancel_and_recreate(self, transfer, picking):
        """Corriger en annulant et recréant le picking"""
        _logger.info("Annulation et recréation du picking %s", picking.name)

        # Annuler l'ancien picking
        picking.action_cancel()

        # Recréer les pickings via le transfert
        if transfer.is_inter_company:
            transfer._create_inter_company_pickings()
        else:
            transfer._create_single_picking()

        # Valider le nouveau picking de sortie
        new_picking = transfer.source_picking_id
        if new_picking and new_picking.state != 'done':
            for move in new_picking.move_lines:
                # Travailler directement avec les move_lines pour éviter l'erreur
                # "Cannot set done quantity from stock move" quand il y a plusieurs lignes
                if move.move_line_ids:
                    for ml in move.move_line_ids:
                        ml.qty_done = ml.product_uom_qty
                else:
                    move.quantity_done = move.product_uom_qty

            ctx = {'skip_backorder': True} if self.skip_backorder else {}
            new_picking.with_context(**ctx).button_validate()

        _logger.info("Nouveau picking %s créé et validé", new_picking.name if new_picking else 'N/A')
