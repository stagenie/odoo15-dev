# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    show_payment_details = fields.Boolean(
        string='Afficher détails paiement',
        default=lambda self: self._get_default_show_payment_details(),
        help="Cocher pour afficher les détails de paiement (mode de règlement, etc.) sur le rapport imprimé."
    )
    show_payment_journal = fields.Boolean(
        string='Afficher journal paiement',
        default=lambda self: self._get_default_show_payment_journal(),
        help="Cocher pour afficher la colonne Journal dans les détails de paiement."
    )
    show_payment_amount = fields.Boolean(
        string='Afficher montant paiement',
        default=lambda self: self._get_default_show_payment_amount(),
        help="Cocher pour afficher la colonne Montant dans les détails de paiement."
    )

    @api.model
    def _get_default_show_payment_details(self):
        """Récupère la valeur par défaut depuis la configuration."""
        return self.env['ir.config_parameter'].sudo().get_param(
            'adi_ab_invoice_reports.default_show_payment_details', 'False'
        ) == 'True'

    @api.model
    def _get_default_show_payment_journal(self):
        """Récupère la valeur par défaut depuis la configuration."""
        return self.env['ir.config_parameter'].sudo().get_param(
            'adi_ab_invoice_reports.default_show_payment_journal', 'False'
        ) == 'True'

    @api.model
    def _get_default_show_payment_amount(self):
        """Récupère la valeur par défaut depuis la configuration."""
        return self.env['ir.config_parameter'].sudo().get_param(
            'adi_ab_invoice_reports.default_show_payment_amount', 'True'
        ) == 'True'
