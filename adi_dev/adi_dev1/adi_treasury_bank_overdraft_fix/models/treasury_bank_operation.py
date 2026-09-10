# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import ValidationError


class TreasuryBankOperationOverdraftFix(models.Model):
    _inherit = 'treasury.bank.operation'

    @api.constrains('operation_type', 'amount', 'bank_id', 'state')
    def _check_bank_balance_on_out(self):
        """Contrôle du découvert sur les sorties bancaires (version corrigée).

        Le champ `treasury.bank.current_balance` est un champ calculé stocké
        alimenté par les opérations à l'état 'posted'. Les contraintes étant
        évaluées APRÈS le recalcul des champs stockés, `current_balance`
        contient déjà le montant de l'opération en cours de validation.

        La version d'origine (adi_treasury_transfer_control) retranchait le
        montant une seconde fois, ce qui refusait à tort toute sortie
        supérieure à la moitié du solde disponible.

        Ici :
          - balance_after  = bank.current_balance         (déjà net de l'opération)
          - balance_before = balance_after + amount       (solde avant opération)

        C'est la même convention que le contrôle du module de base
        adi_treasury_bank (_check_bank_balance).
        """
        for operation in self:
            # Vérifier uniquement pour les opérations de sortie validées
            if operation.operation_type != 'out' or operation.state != 'posted':
                continue

            bank = operation.bank_id
            if not bank:
                continue

            overdraft_limit = getattr(bank, 'overdraft_limit', 0) or 0
            allow_negative = getattr(bank, 'allow_negative_balance', True)

            # current_balance inclut déjà la sortie en cours
            balance_after = bank.current_balance
            balance_before = balance_after + operation.amount
            symbol = operation.currency_id.symbol

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
                            balance_before, symbol,
                            operation.amount, symbol,
                            balance_after, symbol,
                            overdraft_limit, symbol,
                        )
                    )
            else:
                # Solde négatif non autorisé
                if balance_after < 0:
                    raise ValidationError(
                        _("❌ SOLDE INSUFFISANT\n\n"
                          "Compte : %s\n"
                          "Solde actuel : %.2f %s\n"
                          "Montant demandé : %.2f %s\n\n"
                          "Le solde négatif n'est pas autorisé pour ce compte.") % (
                            bank.name,
                            balance_before, symbol,
                            operation.amount, symbol,
                        )
                    )
