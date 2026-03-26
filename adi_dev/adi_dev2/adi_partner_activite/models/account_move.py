# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _check_partner_activite(self):
        """V\u00e9rifie que l'activit\u00e9 du partenaire est renseign\u00e9e si l'option est activ\u00e9e"""
        self.ensure_one()
        is_required = self.env['ir.config_parameter'].sudo().get_param(
            'adi_partner_activite.activite_required_for_invoice', 'True'
        )
        if is_required in ('True', 'true', '1', True):
            if not (self.partner_id.activite or '').strip():
                return ["Activit\u00e9"]
        return []

    def _check_fiscal_and_activite(self):
        """V\u00e9rifie les informations fiscales + activit\u00e9 du partenaire"""
        self.ensure_one()
        missing_fields, warning_fields = self._check_partner_fiscal_info()

        # Ajouter activit\u00e9 aux champs obligatoires si requis
        missing_activite = self._check_partner_activite()
        missing_fields.extend(missing_activite)

        return missing_fields, warning_fields

    def _handle_print_validation(self, report_xmlid):
        """Logique commune de validation avant impression"""
        self.ensure_one()

        if self.invoice_report_type == 'invoice' and self.move_type in ('out_invoice', 'out_refund'):
            missing_fields, warning_fields = self._check_fiscal_and_activite()

            if missing_fields:
                raise UserError(_(
                    "Impossible d'imprimer la facture.\n\n"
                    "Les informations suivantes du client '%s' sont manquantes :\n"
                    "- %s\n\n"
                    "Veuillez compl\u00e9ter la fiche client avant d'imprimer."
                ) % (self.partner_id.name, '\n- '.join(missing_fields)))

            if warning_fields:
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Avertissement'),
                    'res_model': 'invoice.print.warning.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_invoice_id': self.id,
                        'default_report_xmlid': report_xmlid,
                        'default_warning_message': _(
                            "Attention : Le champ '%s' n'est pas renseign\u00e9 pour le client '%s'.\n\n"
                            "Voulez-vous continuer l'impression ?"
                        ) % (', '.join(warning_fields), self.partner_id.name),
                    },
                }

        return self.env.ref(report_xmlid).report_action(self)

    def action_print_ab_invoice(self):
        """Surcharge : imprimer facture avec contr\u00f4le activit\u00e9"""
        self.ensure_one()
        return self._handle_print_validation('adi_ab_invoice_reports.action_report_ab_invoice')

    def action_print_ab_invoice_no_payment(self):
        """Imprimer facture sans paiement avec contr\u00f4le fiscal + activit\u00e9"""
        self.ensure_one()
        return self._handle_print_validation('adi_ab_invoice_reports.action_report_ab_invoice_no_payment')
