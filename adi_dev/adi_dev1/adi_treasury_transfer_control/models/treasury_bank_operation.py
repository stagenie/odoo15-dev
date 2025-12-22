# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class TreasuryBankOperationControl(models.Model):
    _inherit = 'treasury.bank.operation'

    # =========================================================================
    # CONTRAINTES
    # =========================================================================

    @api.constrains('amount')
    def _check_amount_positive(self):
        """Vérifier que le montant est strictement positif"""
        for operation in self:
            if operation.amount <= 0:
                raise ValidationError(
                    _("Le montant de l'opération bancaire doit être strictement positif !\n"
                      "Montant saisi : %s") % operation.amount
                )

    @api.constrains('operation_type', 'amount', 'bank_id', 'state')
    def _check_bank_balance_on_out(self):
        """
        Vérifier que le solde bancaire (avec découvert) est suffisant pour les sorties.
        """
        for operation in self:
            # Vérifier uniquement pour les opérations de sortie validées
            if operation.operation_type == 'out' and operation.state == 'posted':
                bank = operation.bank_id
                if bank:
                    current_balance = bank.current_balance
                    overdraft_limit = getattr(bank, 'overdraft_limit', 0) or 0
                    allow_negative = getattr(bank, 'allow_negative_balance', True)

                    # Calculer le solde après opération
                    balance_after = current_balance - operation.amount

                    # Vérifier si le découvert serait dépassé
                    if allow_negative:
                        if balance_after < -overdraft_limit:
                            raise ValidationError(
                                _("❌ DÉCOUVERT DÉPASSÉ\n\n"
                                  "Compte : %s\n"
                                  "Solde actuel : %.2f %s\n"
                                  "Montant demandé : %.2f %s\n"
                                  "Solde après opération : %.2f %s\n"
                                  "Découvert autorisé : %.2f %s\n\n"
                                  "Cette opération dépasserait le découvert autorisé.") % (
                                    bank.name,
                                    current_balance,
                                    operation.currency_id.symbol,
                                    operation.amount,
                                    operation.currency_id.symbol,
                                    balance_after,
                                    operation.currency_id.symbol,
                                    overdraft_limit,
                                    operation.currency_id.symbol
                                )
                            )
                    else:
                        # Solde négatif non autorisé
                        if current_balance < operation.amount:
                            raise ValidationError(
                                _("❌ SOLDE INSUFFISANT\n\n"
                                  "Compte : %s\n"
                                  "Solde actuel : %.2f %s\n"
                                  "Montant demandé : %.2f %s\n\n"
                                  "Le solde négatif n'est pas autorisé pour ce compte.") % (
                                    bank.name,
                                    current_balance,
                                    operation.currency_id.symbol,
                                    operation.amount,
                                    operation.currency_id.symbol
                                )
                            )
