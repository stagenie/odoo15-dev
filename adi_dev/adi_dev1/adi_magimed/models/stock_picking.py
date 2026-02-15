# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Additional fields for enhanced transfer report
    is_magimed_entry = fields.Boolean(
        string='Bon d\'Entree MAGIMED',
        compute='_compute_magimed_type',
        store=True
    )
    is_magimed_exit = fields.Boolean(
        string='Bon de Sortie MAGIMED',
        compute='_compute_magimed_type',
        store=True
    )
    is_magimed_transfer = fields.Boolean(
        string='Bon de Transfert MAGIMED',
        compute='_compute_magimed_type',
        store=True
    )

    source_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Entrepot Source',
        compute='_compute_warehouses',
        store=True
    )
    dest_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Entrepot Destination',
        compute='_compute_warehouses',
        store=True
    )

    lot_info = fields.Text(
        string='Info Lots',
        compute='_compute_lot_info',
        help="Resume des lots transferes"
    )
    has_lots = fields.Boolean(
        string='Contient des Lots',
        compute='_compute_has_lots'
    )

    entry_reason = fields.Selection([
        ('production', 'Production'),
        ('return', 'Retour'),
        ('adjustment', 'Ajustement'),
        ('other', 'Autre')
    ], string='Motif Entree', default='production')

    exit_reason = fields.Selection([
        ('consumption', 'Consommation'),
        ('scrap', 'Rebut'),
        ('adjustment', 'Ajustement'),
        ('other', 'Autre')
    ], string='Motif Sortie', default='consumption')

    transfer_notes = fields.Text(
        string='Notes de Transfert',
        help="Notes additionnelles pour le transfert"
    )

    @api.depends('date_deadline', 'scheduled_date')
    def _compute_has_deadline_issue(self):
        for picking in self:
            picking.has_deadline_issue = (
                picking.date_deadline and picking.scheduled_date
                and picking.date_deadline < picking.scheduled_date
            ) or False

    @api.depends('picking_type_id')
    def _compute_magimed_type(self):
        for picking in self:
            pt = picking.picking_type_id
            picking.is_magimed_entry = pt.is_magimed_type and pt.magimed_operation == 'entry'
            picking.is_magimed_exit = pt.is_magimed_type and pt.magimed_operation == 'exit'
            picking.is_magimed_transfer = pt.is_magimed_type and pt.magimed_operation == 'transfer'

    @api.depends('location_id', 'location_dest_id')
    def _compute_warehouses(self):
        for picking in self:
            # Find source warehouse
            source_wh = self.env['stock.warehouse'].search([
                ('lot_stock_id', 'parent_of', picking.location_id.id)
            ], limit=1)
            if not source_wh:
                source_wh = self.env['stock.warehouse'].search([
                    ('view_location_id', 'parent_of', picking.location_id.id)
                ], limit=1)
            picking.source_warehouse_id = source_wh.id if source_wh else False

            # Find destination warehouse
            dest_wh = self.env['stock.warehouse'].search([
                ('lot_stock_id', 'parent_of', picking.location_dest_id.id)
            ], limit=1)
            if not dest_wh:
                dest_wh = self.env['stock.warehouse'].search([
                    ('view_location_id', 'parent_of', picking.location_dest_id.id)
                ], limit=1)
            picking.dest_warehouse_id = dest_wh.id if dest_wh else False

    def _compute_lot_info(self):
        for picking in self:
            lot_lines = []
            for move_line in picking.move_line_ids_without_package:
                if move_line.lot_id:
                    expiry = move_line.lot_id.expiration_date
                    expiry_str = expiry.strftime('%d/%m/%Y') if expiry else 'N/A'
                    lot_lines.append(
                        f"{move_line.product_id.display_name}: "
                        f"Lot {move_line.lot_id.name} (Exp: {expiry_str}) - "
                        f"Qte: {move_line.qty_done}"
                    )
            picking.lot_info = '\n'.join(lot_lines) if lot_lines else ''

    def _compute_has_lots(self):
        for picking in self:
            picking.has_lots = any(
                line.lot_id for line in picking.move_line_ids_without_package
            )

    def action_print_bon_entree(self):
        """Print Bon d'Entree report"""
        return self.env.ref('adi_magimed.action_report_bon_entree').report_action(self)

    def action_print_bon_sortie(self):
        """Print Bon de Sortie report"""
        return self.env.ref('adi_magimed.action_report_bon_sortie').report_action(self)

    def action_print_bon_transfert(self):
        """Print Bon de Transfert report"""
        return self.env.ref('adi_magimed.action_report_bon_transfert').report_action(self)

    def _pre_action_done_hook(self):
        """Check for expired lots before validation"""
        res = super()._pre_action_done_hook()
        if res is not True:
            return res

        if self.env.context.get('skip_magimed_expiry'):
            return True

        ICP = self.env['ir.config_parameter'].sudo()
        mode = ICP.get_param('adi_magimed.expiry_control_mode', 'block')
        if mode == 'none':
            return True

        try:
            check_days = int(ICP.get_param('adi_magimed.expiry_check_days', '0'))
        except (ValueError, TypeError):
            check_days = 0

        now = fields.Datetime.now()
        threshold_date = now + timedelta(days=check_days)

        expired_info = []
        expired_lot_ids = []
        for picking in self:
            for ml in picking.move_line_ids_without_package:
                lot = ml.lot_id
                if not lot or not lot.expiration_date:
                    continue
                if lot.expiration_date <= threshold_date:
                    days_remaining = (lot.expiration_date - now).days
                    if days_remaining < 0:
                        status = "EXPIRE depuis %d jour(s)" % abs(days_remaining)
                    elif days_remaining == 0:
                        status = "Expire AUJOURD'HUI"
                    else:
                        status = "Expire dans %d jour(s)" % days_remaining
                    expired_info.append(
                        "- %s | Lot: %s | Exp: %s | %s" % (
                            ml.product_id.display_name,
                            lot.name,
                            lot.expiration_date.strftime('%d/%m/%Y'),
                            status,
                        )
                    )
                    expired_lot_ids.append(lot.id)

        if not expired_info:
            return True

        detail_msg = "\n".join(expired_info)

        if mode == 'block':
            raise UserError(_(
                "Validation impossible : lots expires ou proches de l'expiration detectes.\n\n"
                "%s\n\n"
                "Veuillez retirer ces lots ou modifier la configuration dans "
                "Parametres > MAGIMED > Controle Expiration."
            ) % detail_msg)

        # mode == 'warn': open confirmation wizard
        wizard = self.env['magimed.expiry.confirmation'].create({
            'picking_ids': [(6, 0, self.ids)],
            'lot_ids': [(6, 0, list(set(expired_lot_ids)))],
            'description': detail_msg,
        })
        return {
            'name': _('Lots expires detectes'),
            'type': 'ir.actions.act_window',
            'res_model': 'magimed.expiry.confirmation',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_magimed_type = fields.Boolean(
        string='Type MAGIMED',
        default=False,
        help="Indique si c'est un type d'operation MAGIMED"
    )
    magimed_operation = fields.Selection([
        ('entry', 'Bon d\'Entree'),
        ('exit', 'Bon de Sortie'),
        ('transfer', 'Bon de Transfert')
    ], string='Operation MAGIMED')
