# -*- coding: utf-8 -*-

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Caution management fields
    has_caution = fields.Boolean(
        string='A une Caution',
        default=False,
        help="Cocher si cette facture a une caution a recuperer"
    )
    caution_amount = fields.Monetary(
        string='Montant Caution',
        currency_field='currency_id',
        help="Montant de la caution (si different du total facture)"
    )
    caution_duration_months = fields.Integer(
        string='Duree Caution (mois)',
        default=24,
        help="Duree en mois avant remboursement de la caution"
    )
    caution_refund_date = fields.Date(
        string='Date Remboursement',
        compute='_compute_caution_dates',
        store=True,
        help="Date prevue pour le remboursement de la caution"
    )
    caution_alert_days = fields.Integer(
        string='Alerte Caution (jours)',
        default=30,
        help="Nombre de jours avant echeance pour declencher l'alerte"
    )
    caution_alert_date = fields.Date(
        string='Date Alerte Caution',
        compute='_compute_caution_dates',
        store=True,
        help="Date de declenchement de l'alerte caution"
    )
    caution_status = fields.Selection([
        ('pending', 'En Attente'),
        ('alert', 'A Traiter'),
        ('due', 'Echue'),
        ('refunded', 'Remboursee')
    ], string='Statut Caution', compute='_compute_caution_status', store=True)
    caution_refunded = fields.Boolean(
        string='Caution Remboursee',
        default=False,
        help="Cocher une fois la caution remboursee"
    )
    caution_refund_actual_date = fields.Date(
        string='Date Remboursement Effectif',
        help="Date effective du remboursement de la caution"
    )
    caution_notes = fields.Text(
        string='Notes Caution',
        help="Notes concernant la caution"
    )

    @api.depends('invoice_date', 'caution_duration_months', 'caution_alert_days', 'has_caution')
    def _compute_caution_dates(self):
        for move in self:
            if move.has_caution and move.invoice_date:
                move.caution_refund_date = move.invoice_date + relativedelta(months=move.caution_duration_months)
                move.caution_alert_date = move.caution_refund_date - relativedelta(days=move.caution_alert_days)
            else:
                move.caution_refund_date = False
                move.caution_alert_date = False

    @api.depends('has_caution', 'caution_refunded', 'caution_alert_date', 'caution_refund_date')
    def _compute_caution_status(self):
        today = fields.Date.today()
        for move in self:
            if not move.has_caution:
                move.caution_status = False
            elif move.caution_refunded:
                move.caution_status = 'refunded'
            elif move.caution_refund_date and move.caution_refund_date <= today:
                move.caution_status = 'due'
            elif move.caution_alert_date and move.caution_alert_date <= today:
                move.caution_status = 'alert'
            else:
                move.caution_status = 'pending'

    @api.onchange('has_caution')
    def _onchange_has_caution(self):
        """Set default caution amount when enabling caution"""
        if self.has_caution and not self.caution_amount:
            self.caution_amount = self.amount_total

    def action_mark_caution_refunded(self):
        """Mark caution as refunded"""
        self.write({
            'caution_refunded': True,
            'caution_refund_actual_date': fields.Date.today()
        })
        return True

    def action_send_caution_alert(self):
        """Send caution alert email"""
        template = self.env.ref('adi_magimed.mail_template_caution_alert', raise_if_not_found=False)
        if template:
            for move in self:
                template.send_mail(move.id, force_send=True)
        return True

    @api.model
    def get_caution_alerts(self):
        """Get invoices with caution needing attention"""
        today = fields.Date.today()
        return self.search([
            ('has_caution', '=', True),
            ('caution_refunded', '=', False),
            ('caution_alert_date', '<=', today),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted')
        ], order='caution_refund_date asc')

    @api.model
    def get_caution_stats(self):
        """Get caution statistics for dashboard"""
        today = fields.Date.today()
        caution_invoices = self.search([
            ('has_caution', '=', True),
            ('caution_refunded', '=', False),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted')
        ])

        return {
            'total_count': len(caution_invoices),
            'total_amount': sum(caution_invoices.mapped('caution_amount')),
            'due_count': len(caution_invoices.filtered(lambda m: m.caution_status == 'due')),
            'alert_count': len(caution_invoices.filtered(lambda m: m.caution_status == 'alert')),
            'pending_count': len(caution_invoices.filtered(lambda m: m.caution_status == 'pending')),
        }
