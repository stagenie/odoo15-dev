# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_report_type = fields.Selection(
        related='journal_id.invoice_report_type',
        string='Type de rapport',
        store=True,
        readonly=True,
    )

    def _check_partner_fiscal_info(self):
        """Vérifie que les informations fiscales du client sont renseignées pour les factures"""
        self.ensure_one()
        partner = self.partner_id

        missing_fields = []
        warning_fields = []

        # Champs obligatoires (avec strip pour ignorer les espaces)
        if not (partner.street or '').strip():
            missing_fields.append("Adresse")
        if not (partner.rc or '').strip():
            missing_fields.append("Registre de Commerce (RC)")
        if not (partner.nif or '').strip():
            missing_fields.append("N° Identifiant Fiscal (NIF)")
        if not (partner.ai or '').strip():
            missing_fields.append("Article d'Imposition (AI)")

        # Champ avec avertissement (NIS)
        if not (partner.nis or '').strip():
            warning_fields.append("NIS")

        return missing_fields, warning_fields

    def action_print_ab_invoice(self):
        """Imprimer le rapport AB Facture avec validation des informations fiscales"""
        self.ensure_one()

        # Vérifier les informations fiscales pour les factures de type "invoice"
        if self.invoice_report_type == 'invoice' and self.move_type in ('out_invoice', 'out_refund'):
            missing_fields, warning_fields = self._check_partner_fiscal_info()

            if missing_fields:
                raise UserError(_(
                    "Impossible d'imprimer la facture.\n\n"
                    "Les informations suivantes du client '%s' sont manquantes :\n"
                    "- %s\n\n"
                    "Veuillez compléter la fiche client avant d'imprimer."
                ) % (self.partner_id.name, '\n- '.join(missing_fields)))

            # Avertissement pour NIS (non bloquant)
            if warning_fields:
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Avertissement'),
                    'res_model': 'invoice.print.warning.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_invoice_id': self.id,
                        'default_warning_message': _(
                            "Attention : Le champ '%s' n'est pas renseigné pour le client '%s'.\n\n"
                            "Voulez-vous continuer l'impression ?"
                        ) % (', '.join(warning_fields), self.partner_id.name),
                    },
                }

        return self.env.ref('adi_ab_invoice_reports.action_report_ab_invoice').report_action(self)

    def action_print_vente(self):
        """Imprimer le rapport Vente"""
        self.ensure_one()
        return self.env.ref('adi_ab_invoice_reports.action_report_ab_vente').report_action(self)

    def action_print_vente_ttc(self):
        """Imprimer le rapport Vente TTC"""
        self.ensure_one()
        return self.env.ref('adi_ab_invoice_reports.action_report_ab_vente_ttc').report_action(self)
