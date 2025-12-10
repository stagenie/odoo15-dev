# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockTransferBackorder(models.Model):
    """Extension du modele de transfert pour gerer les receptions partielles"""
    _inherit = 'adi.stock.transfer'

    # Redefinir les etats pour inclure 'partial'
    state = fields.Selection(
        selection_add=[
            ('partial', 'Reception Partielle'),
        ],
        ondelete={'partial': 'set default'}
    )

    # Champs calcules pour les reliquats
    backorder_count = fields.Integer(
        'Nombre de Reliquats',
        compute='_compute_backorder_count'
    )

    total_qty_backorder = fields.Float(
        'Total Reliquat',
        compute='_compute_qty_backorder',
        store=True,
        help="Quantite restante a recevoir (envoyee - recue)"
    )

    has_backorder = fields.Boolean(
        'A des Reliquats',
        compute='_compute_has_backorder',
        store=True
    )

    # Reference au transfert parent (pour les reliquats crees)
    parent_transfer_id = fields.Many2one(
        'adi.stock.transfer',
        'Transfert Parent',
        readonly=True,
        help="Reference au transfert original si ce transfert est un reliquat"
    )

    child_transfer_ids = fields.One2many(
        'adi.stock.transfer',
        'parent_transfer_id',
        'Transferts Reliquats',
        readonly=True
    )

    # Quantite en transit pour suivi
    qty_in_transit = fields.Float(
        'Quantite en Transit',
        compute='_compute_qty_in_transit',
        store=True
    )

    @api.depends('transfer_line_ids.qty_sent', 'transfer_line_ids.qty_received')
    def _compute_qty_backorder(self):
        """Calcul du total des reliquats"""
        for record in self:
            total_backorder = 0.0
            for line in record.transfer_line_ids:
                # Reliquat = quantite envoyee - quantite recue
                backorder = max(0, line.qty_sent - line.qty_received)
                total_backorder += backorder
            record.total_qty_backorder = total_backorder

    @api.depends('total_qty_backorder')
    def _compute_has_backorder(self):
        """Determine si le transfert a des reliquats"""
        for record in self:
            record.has_backorder = record.total_qty_backorder > 0

    def _compute_backorder_count(self):
        """Compte le nombre de transferts reliquats"""
        for record in self:
            record.backorder_count = len(record.child_transfer_ids)

    @api.depends('transfer_line_ids.qty_sent', 'transfer_line_ids.qty_received', 'state')
    def _compute_qty_in_transit(self):
        """Calcul de la quantite en transit"""
        for record in self:
            if record.state == 'in_transit':
                # En transit = envoye - recu
                record.qty_in_transit = sum(
                    max(0, line.qty_sent - line.qty_received)
                    for line in record.transfer_line_ids
                )
            else:
                record.qty_in_transit = 0.0

    def action_receive(self):
        """Ouvrir le wizard de reception partielle"""
        self.ensure_one()
        if self.state != 'in_transit':
            raise UserError(_("Le transfert doit etre en transit pour valider une reception!"))

        # Creer le wizard
        wizard = self.env['adi.stock.transfer.receive.wizard'].create({
            'transfer_id': self.id,
        })

        # Creer les lignes du wizard avec les donnees actuelles
        for line in self.transfer_line_ids:
            if line.qty_sent > 0:
                qty_remaining = line.qty_sent - line.qty_received
                self.env['adi.stock.transfer.receive.wizard.line'].create({
                    'wizard_id': wizard.id,
                    'transfer_line_id': line.id,
                    'product_id': line.product_id.id,
                    'product_uom_id': line.product_uom_id.id,
                    'qty_sent': line.qty_sent,
                    'qty_already_received': line.qty_received,
                    'qty_to_receive': qty_remaining,
                })

        return {
            'name': _('Reception du Transfert'),
            'type': 'ir.actions.act_window',
            'res_model': 'adi.stock.transfer.receive.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

    def action_process_backorder(self):
        """Traiter les reliquats du transfert"""
        self.ensure_one()
        if not self.has_backorder:
            raise UserError(_("Ce transfert n'a pas de reliquat a traiter!"))

        # Creer le wizard
        wizard = self.env['adi.stock.transfer.discrepancy.wizard'].create({
            'transfer_id': self.id,
        })

        # Creer les lignes du wizard pour traitement des ecarts
        for line in self.transfer_line_ids:
            qty_backorder = line.qty_sent - line.qty_received
            if qty_backorder > 0:
                self.env['adi.stock.transfer.discrepancy.wizard.line'].create({
                    'wizard_id': wizard.id,
                    'transfer_line_id': line.id,
                    'product_id': line.product_id.id,
                    'product_uom_id': line.product_uom_id.id,
                    'qty_sent': line.qty_sent,
                    'qty_received': line.qty_received,
                    'qty_backorder': qty_backorder,
                    'action': 'return_sender',
                })

        return {
            'name': _('Traitement des Reliquats'),
            'type': 'ir.actions.act_window',
            'res_model': 'adi.stock.transfer.discrepancy.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

    def action_receive_partial(self, wizard):
        """Effectuer une reception partielle depuis le wizard"""
        self.ensure_one()

        # Mettre a jour les quantites recues sur les lignes
        for wiz_line in wizard.line_ids:
            if wiz_line.transfer_line_id:
                new_qty_received = wiz_line.qty_already_received + wiz_line.qty_to_receive
                wiz_line.transfer_line_id.qty_received = new_qty_received

        # Verifier s'il reste des reliquats
        has_remaining = any(
            line.qty_sent > line.qty_received
            for line in self.transfer_line_ids
        )

        if has_remaining:
            self.state = 'partial'
            self.message_post(body=_("Reception partielle enregistree - Reliquats a traiter"))
        else:
            # Tout a ete recu
            self._finalize_reception()

    def _finalize_reception(self):
        """Finaliser la reception et valider le picking d'entree"""
        self.ensure_one()

        # Valider le picking d'entree
        if self.dest_picking_id and self.dest_picking_id.state not in ('done', 'cancel'):
            for move in self.dest_picking_id.move_lines:
                transfer_line = self.transfer_line_ids.filtered(
                    lambda l: l.product_id.id == move.product_id.id
                )
                if transfer_line:
                    move.quantity_done = transfer_line[0].qty_received
            self.dest_picking_id.with_context(skip_backorder=True).button_validate()

        self.state = 'done'
        self.message_post(body=_("Reception complete - Transfert termine"))

    def action_view_backorders(self):
        """Afficher les transferts reliquats associes"""
        self.ensure_one()
        action = self.env.ref('adi_stock_transfer.action_stock_transfer').read()[0]
        action['domain'] = [('parent_transfer_id', '=', self.id)]
        action['context'] = {'default_parent_transfer_id': self.id}
        return action


class StockTransferLineBackorder(models.Model):
    """Extension des lignes de transfert pour les reliquats"""
    _inherit = 'adi.stock.transfer.line'

    # Redefinir le calcul du reliquat base sur qty_sent
    @api.depends('qty_sent', 'qty_received')
    def _compute_qty_remaining(self):
        """Calcul du reliquat: quantite envoyee - quantite recue"""
        for line in self:
            line.qty_remaining = max(0, line.qty_sent - line.qty_received)

    # Mettre a jour l'etat de la ligne
    @api.depends('quantity', 'qty_sent', 'qty_received')
    def _compute_line_state(self):
        """Calcul de l'etat de la ligne avec gestion des partiels"""
        for line in self:
            if line.qty_received >= line.qty_sent and line.qty_sent > 0:
                line.line_state = 'done'
            elif line.qty_received > 0:
                line.line_state = 'partial'
            elif line.qty_sent > 0:
                line.line_state = 'sent'
            else:
                line.line_state = 'pending'
