# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # ====== LIGNES DE COSTING ======
    costing_line_ids = fields.One2many(
        'project.costing.line',
        'order_id',
        string='Lignes de costing',
        copy=True
    )

    # ====== COMPTEUR POUR SMART BUTTON ======
    costing_line_count = fields.Integer(
        string='Nombre de lignes costing',
        compute='_compute_costing_line_count'
    )

    # ====== TOTAUX COSTING ======
    costing_total_cost = fields.Monetary(
        string='Total Coût',
        compute='_compute_costing_totals',
        store=True,
        currency_field='currency_id'
    )

    costing_total_sale = fields.Monetary(
        string='Total Vente (Costing)',
        compute='_compute_costing_totals',
        store=True,
        currency_field='currency_id'
    )

    costing_total_margin = fields.Monetary(
        string='Marge Totale (Costing)',
        compute='_compute_costing_totals',
        store=True,
        currency_field='currency_id'
    )

    costing_total_equipment_margin = fields.Monetary(
        string='Total Marge Équipement',
        compute='_compute_costing_totals',
        store=True,
        currency_field='currency_id'
    )

    costing_total_labor_margin = fields.Monetary(
        string="Total Main d'Oeuvre",
        compute='_compute_costing_totals',
        store=True,
        currency_field='currency_id'
    )

    costing_margin_percent = fields.Float(
        string='% Marge Global',
        compute='_compute_costing_totals',
        store=True,
        digits=(16, 2)
    )

    # ====== INDICATEUR DE SYNCHRONISATION ======
    costing_all_synced = fields.Boolean(
        string='Tout synchronisé',
        compute='_compute_costing_sync_status'
    )

    costing_unsynced_count = fields.Integer(
        string='Lignes non synchronisées',
        compute='_compute_costing_sync_status'
    )

    # ====== METHODES COMPUTE ======

    @api.depends('costing_line_ids')
    def _compute_costing_line_count(self):
        for order in self:
            order.costing_line_count = len(order.costing_line_ids)

    @api.depends(
        'costing_line_ids.subtotal_cost',
        'costing_line_ids.subtotal_sale',
        'costing_line_ids.margin_total',
        'costing_line_ids.total_equipment_margin',
        'costing_line_ids.total_labor_margin'
    )
    def _compute_costing_totals(self):
        for order in self:
            lines = order.costing_line_ids
            order.costing_total_cost = sum(lines.mapped('subtotal_cost'))
            order.costing_total_sale = sum(lines.mapped('subtotal_sale'))
            order.costing_total_margin = sum(lines.mapped('margin_total'))
            order.costing_total_equipment_margin = sum(lines.mapped('total_equipment_margin'))
            order.costing_total_labor_margin = sum(lines.mapped('total_labor_margin'))

            # % marge global (sur le coût)
            if order.costing_total_cost > 0:
                order.costing_margin_percent = (
                    order.costing_total_margin / order.costing_total_cost
                ) * 100
            else:
                order.costing_margin_percent = 0.0

    @api.depends('costing_line_ids.is_synced')
    def _compute_costing_sync_status(self):
        for order in self:
            unsynced = order.costing_line_ids.filtered(lambda l: not l.is_synced)
            order.costing_unsynced_count = len(unsynced)
            order.costing_all_synced = len(unsynced) == 0 and len(order.costing_line_ids) > 0

    # ====== ACTIONS ======

    def action_view_costing_lines(self):
        """Ouvre la vue des lignes de costing"""
        self.ensure_one()
        return {
            'name': _('Calcul Costing Projet'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.costing.line',
            'view_mode': 'tree,form',
            'domain': [('order_id', '=', self.id)],
            'context': {
                'default_order_id': self.id,
                'search_default_order_id': self.id,
            },
        }

    def action_open_costing_wizard(self):
        """Ouvre le wizard de saisie costing"""
        self.ensure_one()
        return {
            'name': _('Saisie Costing Projet'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.costing.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
            },
        }

    def action_sync_all_costing(self):
        """Synchronise toutes les lignes de costing non synchronisées"""
        self.ensure_one()

        if self.state not in ('draft', 'sent'):
            raise UserError(_(
                "La synchronisation n'est possible qu'en état Devis ou Devis envoyé."
            ))

        unsynced_lines = self.costing_line_ids.filtered(lambda l: not l.is_synced)

        for line in unsynced_lines:
            if line.sale_line_id:
                line.action_sync_to_sale_line()
            else:
                line.action_create_sale_line()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Synchronisation effectuée'),
                'message': _('%d ligne(s) synchronisée(s)') % len(unsynced_lines),
                'type': 'success',
                'sticky': False,
            }
        }
