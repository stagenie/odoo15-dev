# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import UserError


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, res_ids=None, data=None):
        """Surcharge pour valider les informations fiscales avant impression"""

        # Liste des rapports AB Facture concernés
        ab_invoice_reports = [
            'l10n_dz_droit_timbre.adi_report_invoice',
            'adi_ab_invoice_reports.action_report_ab_invoice',
        ]

        # Vérifier si c'est un rapport AB Facture
        if self.report_name in ab_invoice_reports or 'adi_report_invoice' in (self.report_name or ''):
            if res_ids:
                moves = self.env['account.move'].browse(res_ids)
                for move in moves:
                    # Vérifier uniquement pour les factures de type "invoice"
                    if (move.invoice_report_type == 'invoice' and
                        move.move_type in ('out_invoice', 'out_refund')):

                        missing_fields = self._check_partner_fiscal_info(move)

                        if missing_fields:
                            raise UserError(_(
                                "Impossible d'imprimer la facture '%s'.\n\n"
                                "Les informations suivantes du client '%s' sont manquantes :\n"
                                "- %s\n\n"
                                "Veuillez compléter la fiche client avant d'imprimer."
                            ) % (move.name, move.partner_id.name, '\n- '.join(missing_fields)))

        return super()._render_qweb_pdf(res_ids=res_ids, data=data)

    def _check_partner_fiscal_info(self, move):
        """Vérifie les informations fiscales du partenaire"""
        partner = move.partner_id
        missing_fields = []

        if not (partner.street or '').strip():
            missing_fields.append("Adresse")
        if not (partner.rc or '').strip():
            missing_fields.append("Registre de Commerce (RC)")
        if not (partner.nif or '').strip():
            missing_fields.append("N° Identifiant Fiscal (NIF)")
        if not (partner.ai or '').strip():
            missing_fields.append("Article d'Imposition (AI)")

        return missing_fields
