# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_method_display = fields.Char(
        string='Mode de règlement',
        compute='_compute_payment_method_display',
        store=False
    )

    @api.depends('payment_id', 'payment_id.payment_method_line_id')
    def _compute_payment_method_display(self):
        """
        Calcule le mode de règlement à afficher sur la facture
        basé sur les paiements enregistrés et le module adi_bank_payment_mode
        """
        for move in self:
            payment_info = []

            # Rechercher les paiements liés à cette facture
            payments = self.env['account.payment'].search([
                ('reconciled_invoice_ids', 'in', move.id)
            ])

            for payment in payments:
                method_name = payment.payment_method_line_id.name if payment.payment_method_line_id else ''
                payment_date = payment.date.strftime('%d/%m/%Y') if payment.date else ''

                # Si c'est un chèque, essayer de récupérer le numéro depuis adi_bank_payment_mode
                if 'chèque' in method_name.lower() or 'cheque' in method_name.lower():
                    # Vérifier si le module adi_bank_payment_mode est installé
                    if hasattr(payment, 'check_number'):
                        check_num = payment.check_number or ''
                        payment_info.append(f"Chèque N° {check_num} - Date: {payment_date}")
                    else:
                        payment_info.append(f"Chèque - Date: {payment_date}")
                elif 'espèce' in method_name.lower() or 'cash' in method_name.lower():
                    payment_info.append(f"Espèce - Date: {payment_date}")
                else:
                    payment_info.append(f"{method_name} - Date: {payment_date}")

            move.payment_method_display = ', '.join(payment_info) if payment_info else ''
