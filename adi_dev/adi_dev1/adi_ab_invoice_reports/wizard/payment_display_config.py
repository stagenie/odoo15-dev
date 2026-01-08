# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PaymentDisplayConfig(models.TransientModel):
    _name = 'payment.display.config'
    _description = 'Configuration Affichage Détails Paiement'

    show_payment_details = fields.Boolean(
        string='Afficher détails paiement',
        default=lambda self: self._get_default_show_payment_details(),
        help="Afficher les détails de paiement sur les factures."
    )
    show_payment_journal = fields.Boolean(
        string='Afficher journal paiement',
        default=lambda self: self._get_default_show_payment_journal(),
        help="Afficher la colonne Journal dans les détails de paiement."
    )
    show_payment_amount = fields.Boolean(
        string='Afficher montant paiement',
        default=lambda self: self._get_default_show_payment_amount(),
        help="Afficher la colonne Montant dans les détails de paiement."
    )

    @api.model
    def _get_default_show_payment_details(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'adi_ab_invoice_reports.default_show_payment_details', 'False'
        ) == 'True'

    @api.model
    def _get_default_show_payment_journal(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'adi_ab_invoice_reports.default_show_payment_journal', 'False'
        ) == 'True'

    @api.model
    def _get_default_show_payment_amount(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'adi_ab_invoice_reports.default_show_payment_amount', 'True'
        ) == 'True'

    def action_save_config(self):
        """Sauvegarder la configuration par défaut."""
        self.ensure_one()
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('adi_ab_invoice_reports.default_show_payment_details', str(self.show_payment_details))
        ICP.set_param('adi_ab_invoice_reports.default_show_payment_journal', str(self.show_payment_journal))
        ICP.set_param('adi_ab_invoice_reports.default_show_payment_amount', str(self.show_payment_amount))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Configuration sauvegardée',
                'message': 'Les paramètres par défaut ont été enregistrés. Les nouvelles factures utiliseront cette configuration.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_update_all_invoices(self):
        """Mettre à jour toutes les factures existantes avec la configuration actuelle."""
        self.ensure_one()

        # Mettre à jour toutes les factures
        invoices = self.env['account.move'].search([
            ('move_type', 'in', ['out_invoice', 'out_refund', 'in_invoice', 'in_refund'])
        ])

        if invoices:
            invoices.write({
                'show_payment_details': self.show_payment_details,
                'show_payment_journal': self.show_payment_journal,
                'show_payment_amount': self.show_payment_amount,
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Mise à jour terminée',
                'message': f'{len(invoices)} facture(s) mise(s) à jour avec la nouvelle configuration.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_save_and_update_all(self):
        """Sauvegarder la configuration et mettre à jour toutes les factures."""
        self.action_save_config()
        return self.action_update_all_invoices()
