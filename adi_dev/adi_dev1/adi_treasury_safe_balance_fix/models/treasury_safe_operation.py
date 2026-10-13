# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import ValidationError


class TreasurySafeOperationBalanceFix(models.Model):
    _inherit = 'treasury.safe.operation'

    @api.constrains('operation_type', 'amount', 'safe_id', 'state')
    def _check_safe_balance_on_out(self):
        """Contrôle du solde sur les sorties de coffre (version corrigée).

        Le champ `treasury.safe.current_balance` est un champ calculé stocké
        alimenté par les opérations à l'état 'done'. Les contraintes étant
        évaluées APRÈS le recalcul des champs stockés :
          - à l'état 'confirmed', current_balance n'inclut pas la sortie ;
          - à l'état 'done', current_balance inclut déjà la sortie.

        La version d'origine (adi_treasury_transfer_control) comparait
        current_balance au montant dans les deux cas, ce qui retranchait la
        sortie une seconde fois à l'état 'done' et refusait à tort toute
        sortie supérieure à la moitié du solde du coffre.
        """
        for operation in self:
            if operation.operation_type not in ('bank_out', 'other_out'):
                continue
            if operation.state not in ('confirmed', 'done'):
                continue

            safe = operation.safe_id
            if not safe or getattr(safe, 'allow_negative_balance', False):
                continue

            # Forcer le recalcul du solde
            safe._compute_current_balance()
            if operation.state == 'done':
                # current_balance inclut déjà la sortie en cours
                balance_after = safe.current_balance
                balance_before = balance_after + operation.amount
            else:
                balance_before = safe.current_balance
                balance_after = balance_before - operation.amount

            if balance_after < 0:
                symbol = operation.currency_id.symbol
                raise ValidationError(
                    _("❌ SOLDE INSUFFISANT\n\n"
                      "Coffre : %s\n"
                      "Solde actuel : %.2f %s\n"
                      "Montant demandé : %.2f %s\n"
                      "Manque : %.2f %s\n\n"
                      "Cette opération ne peut pas être effectuée.") % (
                        safe.name,
                        balance_before, symbol,
                        operation.amount, symbol,
                        -balance_after, symbol,
                    )
                )
