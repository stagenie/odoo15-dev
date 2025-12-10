# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockTransferReceiveWizard(models.TransientModel):
    """Wizard de reception partielle des transferts"""
    _name = 'adi.stock.transfer.receive.wizard'
    _description = 'Reception du Transfert'

    transfer_id = fields.Many2one(
        'adi.stock.transfer',
        'Transfert',
        required=True,
        readonly=True
    )

    line_ids = fields.One2many(
        'adi.stock.transfer.receive.wizard.line',
        'wizard_id',
        'Lignes'
    )

    def action_confirm(self):
        """Confirmer la reception partielle"""
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("Aucune ligne a traiter!"))

        self.transfer_id.action_receive_partial(self)
        return {'type': 'ir.actions.act_window_close'}


class StockTransferReceiveWizardLine(models.TransientModel):
    """Ligne du wizard de reception"""
    _name = 'adi.stock.transfer.receive.wizard.line'
    _description = 'Ligne Reception Transfert'

    wizard_id = fields.Many2one(
        'adi.stock.transfer.receive.wizard',
        'Wizard',
        required=True,
        ondelete='cascade'
    )

    transfer_line_id = fields.Many2one(
        'adi.stock.transfer.line',
        'Ligne Transfert',
        required=True,
        readonly=True
    )

    product_id = fields.Many2one(
        'product.product',
        'Produit',
        readonly=True
    )

    product_uom_id = fields.Many2one(
        'uom.uom',
        'Unite',
        readonly=True
    )

    qty_sent = fields.Float(
        'Qte Envoyee',
        readonly=True
    )

    qty_already_received = fields.Float(
        'Deja Recu',
        readonly=True
    )

    qty_to_receive = fields.Float(
        'A Recevoir',
        help="Quantite a recevoir maintenant"
    )

    qty_remaining = fields.Float(
        'Reste',
        compute='_compute_qty_remaining',
        readonly=True
    )

    @api.depends('qty_sent', 'qty_already_received', 'qty_to_receive')
    def _compute_qty_remaining(self):
        """Calcul de la quantite restante apres reception"""
        for line in self:
            line.qty_remaining = line.qty_sent - line.qty_already_received - line.qty_to_receive

    @api.constrains('qty_to_receive')
    def _check_qty_to_receive(self):
        """Verification de la quantite a recevoir"""
        for line in self:
            max_receivable = line.qty_sent - line.qty_already_received
            if line.qty_to_receive < 0:
                raise UserError(_(
                    "La quantite a recevoir ne peut pas etre negative pour '%s'!"
                ) % line.product_id.display_name)
            if line.qty_to_receive > max_receivable:
                raise UserError(_(
                    "La quantite a recevoir (%.2f) ne peut pas depasser la quantite restante (%.2f) pour '%s'!"
                ) % (line.qty_to_receive, max_receivable, line.product_id.display_name))


class StockTransferDiscrepancyWizard(models.TransientModel):
    """Wizard de traitement des ecarts/reliquats"""
    _name = 'adi.stock.transfer.discrepancy.wizard'
    _description = 'Traitement des Reliquats'

    transfer_id = fields.Many2one(
        'adi.stock.transfer',
        'Transfert',
        required=True,
        readonly=True
    )

    line_ids = fields.One2many(
        'adi.stock.transfer.discrepancy.wizard.line',
        'wizard_id',
        'Lignes'
    )

    def action_confirm(self):
        """Traiter les reliquats selon les actions choisies"""
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("Aucune ligne a traiter!"))

        for line in self.line_ids:
            if line.qty_backorder > 0:
                line._process_discrepancy()

        # Terminer le transfert original
        self.transfer_id.state = 'done'
        self.transfer_id.message_post(body=_("Reliquats traites - Transfert termine"))

        return {'type': 'ir.actions.act_window_close'}


class StockTransferDiscrepancyWizardLine(models.TransientModel):
    """Ligne du wizard de traitement des ecarts"""
    _name = 'adi.stock.transfer.discrepancy.wizard.line'
    _description = 'Ligne Traitement Ecart'

    wizard_id = fields.Many2one(
        'adi.stock.transfer.discrepancy.wizard',
        'Wizard',
        required=True,
        ondelete='cascade'
    )

    transfer_line_id = fields.Many2one(
        'adi.stock.transfer.line',
        'Ligne Transfert',
        required=True,
        readonly=True
    )

    product_id = fields.Many2one(
        'product.product',
        'Produit',
        readonly=True
    )

    product_uom_id = fields.Many2one(
        'uom.uom',
        'Unite',
        readonly=True
    )

    qty_sent = fields.Float(
        'Qte Envoyee',
        readonly=True
    )

    qty_received = fields.Float(
        'Qte Recue',
        readonly=True
    )

    qty_backorder = fields.Float(
        'Reliquat',
        readonly=True
    )

    action = fields.Selection([
        ('return_sender', 'Retour Expediteur'),
        ('inventory_adjustment', 'Ajustement Inventaire'),
        ('pending', 'Reporter (Envoi Ulterieur)'),
    ], string='Action', required=True, default='return_sender')

    note = fields.Text('Note')

    def _process_discrepancy(self):
        """Traiter l'ecart selon l'action choisie"""
        self.ensure_one()
        transfer = self.wizard_id.transfer_id

        if self.action == 'return_sender':
            self._action_return_sender(transfer)
        elif self.action == 'inventory_adjustment':
            self._action_inventory_adjustment(transfer)
        elif self.action == 'pending':
            self._action_pending(transfer)

    def _action_return_sender(self, transfer):
        """Retourner les produits a l'expediteur (Transit -> Source)"""
        if not transfer.transit_location_id:
            return

        # Creer un mouvement de stock du transit vers la source
        move_vals = {
            'name': _('Retour expediteur - %s') % self.product_id.name,
            'product_id': self.product_id.id,
            'product_uom_qty': self.qty_backorder,
            'product_uom': self.product_uom_id.id,
            'location_id': transfer.transit_location_id.id,
            'location_dest_id': transfer.source_location_id.id,
            'company_id': transfer.source_company_id.id,
            'origin': transfer.name,
        }

        move = self.env['stock.move'].create(move_vals)
        move._action_confirm()
        move.quantity_done = self.qty_backorder
        move._action_done()

        transfer.message_post(body=_(
            "Retour expediteur: %(qty)s %(uom)s de %(product)s"
        ) % {
            'qty': self.qty_backorder,
            'uom': self.product_uom_id.name,
            'product': self.product_id.name
        })

    def _action_inventory_adjustment(self, transfer):
        """Ajustement d'inventaire (perte en transit)"""
        if not transfer.transit_location_id:
            return

        # Chercher l'emplacement de perte d'inventaire
        inventory_loss_location = self.env.ref(
            'stock.stock_location_inventory',
            raise_if_not_found=False
        )

        if not inventory_loss_location:
            inventory_loss_location = self.env['stock.location'].search([
                ('usage', '=', 'inventory'),
            ], limit=1)

        if not inventory_loss_location:
            raise UserError(_("Aucun emplacement de perte d'inventaire trouve!"))

        # Creer un mouvement de stock du transit vers l'inventaire
        move_vals = {
            'name': _('Ajustement inventaire - %s') % self.product_id.name,
            'product_id': self.product_id.id,
            'product_uom_qty': self.qty_backorder,
            'product_uom': self.product_uom_id.id,
            'location_id': transfer.transit_location_id.id,
            'location_dest_id': inventory_loss_location.id,
            'company_id': transfer.source_company_id.id,
            'origin': transfer.name,
        }

        move = self.env['stock.move'].create(move_vals)
        move._action_confirm()
        move.quantity_done = self.qty_backorder
        move._action_done()

        transfer.message_post(body=_(
            "Ajustement inventaire: %(qty)s %(uom)s de %(product)s - %(note)s"
        ) % {
            'qty': self.qty_backorder,
            'uom': self.product_uom_id.name,
            'product': self.product_id.name,
            'note': self.note or _('Ecart en transit')
        })

    def _action_pending(self, transfer):
        """Reporter l'ecart pour traitement ulterieur"""
        # Creer un nouveau transfert pour le reliquat
        new_transfer_vals = {
            'parent_transfer_id': transfer.id,
            'source_company_id': transfer.source_company_id.id,
            'dest_company_id': transfer.dest_company_id.id,
            'source_warehouse_id': transfer.source_warehouse_id.id,
            'dest_warehouse_id': transfer.dest_warehouse_id.id,
            'source_location_id': transfer.source_location_id.id,
            'dest_location_id': transfer.dest_location_id.id,
            'requester_id': transfer.requester_id.id,
            'note': _('Reliquat du transfert %s') % transfer.name,
        }

        new_transfer = self.env['adi.stock.transfer'].create(new_transfer_vals)

        # Ajouter la ligne
        self.env['adi.stock.transfer.line'].create({
            'transfer_id': new_transfer.id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'quantity': self.qty_backorder,
        })

        transfer.message_post(body=_(
            "Reliquat reporte: %(qty)s %(uom)s de %(product)s -> Transfert %(ref)s"
        ) % {
            'qty': self.qty_backorder,
            'uom': self.product_uom_id.name,
            'product': self.product_id.name,
            'ref': new_transfer.name
        })
