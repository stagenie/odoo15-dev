# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class TreasurySafeOperationControl(models.Model):
    _inherit = 'treasury.safe.operation'

    # =========================================================================
    # CONTRAINTES
    # =========================================================================

    @api.constrains('amount')
    def _check_amount_positive(self):
        """Vérifier que le montant est strictement positif"""
        for operation in self:
            if operation.amount <= 0:
                raise ValidationError(
                    _("Le montant de l'opération doit être strictement positif !\n"
                      "Montant saisi : %s") % operation.amount
                )

    @api.constrains('operation_type', 'amount', 'safe_id', 'state')
    def _check_safe_balance_on_out(self):
        """
        Vérifier que le solde du coffre est suffisant pour les sorties.
        Cette vérification est faite lors de la création/modification.
        """
        for operation in self:
            # Vérifier uniquement pour les opérations de sortie en cours de validation
            if operation.operation_type in ['bank_out', 'other_out']:
                if operation.state in ['confirmed', 'done']:
                    # Calculer le solde actuel du coffre
                    safe = operation.safe_id
                    if safe:
                        # Forcer le recalcul du solde
                        safe._compute_current_balance()
                        current_balance = safe.current_balance

                        # Vérifier si autorisation de solde négatif
                        allow_negative = getattr(safe, 'allow_negative_balance', False)

                        if not allow_negative and current_balance < operation.amount:
                            raise ValidationError(
                                _("❌ SOLDE INSUFFISANT\n\n"
                                  "Coffre : %s\n"
                                  "Solde actuel : %.2f %s\n"
                                  "Montant demandé : %.2f %s\n"
                                  "Manque : %.2f %s\n\n"
                                  "Cette opération ne peut pas être effectuée.") % (
                                    safe.name,
                                    current_balance,
                                    operation.currency_id.symbol,
                                    operation.amount,
                                    operation.currency_id.symbol,
                                    operation.amount - current_balance,
                                    operation.currency_id.symbol
                                )
                            )

    # =========================================================================
    # SURCHARGE DES MÉTHODES
    # =========================================================================

    def action_confirm(self):
        """Surcharge pour ajouter la vérification de solde"""
        for operation in self:
            if operation.state != 'draft':
                raise UserError(_("Seules les opérations en brouillon peuvent être confirmées."))

            # Vérifier le solde pour les sorties
            if operation.operation_type in ['bank_out', 'other_out']:
                safe = operation.safe_id
                if safe:
                    safe._compute_current_balance()
                    current_balance = safe.current_balance
                    allow_negative = getattr(safe, 'allow_negative_balance', False)

                    if not allow_negative and current_balance < operation.amount:
                        raise UserError(
                            _("❌ SOLDE INSUFFISANT\n\n"
                              "Coffre : %s\n"
                              "Solde disponible : %.2f %s\n"
                              "Montant demandé : %.2f %s\n"
                              "Manque : %.2f %s\n\n"
                              "Veuillez réduire le montant ou approvisionner le coffre.") % (
                                safe.name,
                                current_balance,
                                operation.currency_id.symbol,
                                operation.amount,
                                operation.currency_id.symbol,
                                operation.amount - current_balance,
                                operation.currency_id.symbol
                            )
                        )

                    _logger.info(
                        "Opération coffre confirmée: %s - Sortie de %.2f sur %s (Solde: %.2f)",
                        operation.name, operation.amount, safe.name, current_balance
                    )

            operation.state = 'confirmed'
            operation.message_post(body=_("Opération confirmée par %s") % self.env.user.name)

        return True

    def action_done(self):
        """Surcharge pour re-vérifier le solde avant validation finale"""
        for operation in self:
            if operation.state != 'confirmed':
                raise UserError(_("Seules les opérations confirmées peuvent être effectuées."))

            # Re-vérifier le solde pour les sorties (au cas où il aurait changé)
            if operation.operation_type in ['bank_out', 'other_out']:
                safe = operation.safe_id
                if safe:
                    safe._compute_current_balance()
                    current_balance = safe.current_balance
                    allow_negative = getattr(safe, 'allow_negative_balance', False)

                    if not allow_negative and current_balance < operation.amount:
                        raise UserError(
                            _("❌ SOLDE INSUFFISANT (vérification finale)\n\n"
                              "Le solde du coffre '%s' a changé depuis la confirmation.\n"
                              "Solde actuel : %.2f %s\n"
                              "Montant demandé : %.2f %s\n\n"
                              "Veuillez annuler et recréer l'opération.") % (
                                safe.name,
                                current_balance,
                                operation.currency_id.symbol,
                                operation.amount,
                                operation.currency_id.symbol
                            )
                        )

            operation.write({
                'state': 'done',
                'validated_by': self.env.user.id
            })

            # Message détaillé
            operation_label = dict(operation._fields['operation_type'].selection).get(
                operation.operation_type, operation.operation_type
            )
            msg = _("Opération %s : %.2f %s") % (
                operation_label,
                operation.amount,
                operation.currency_id.symbol
            )

            if operation.bank_reference:
                msg += _(" (Réf: %s)") % operation.bank_reference

            operation.safe_id.message_post(body=msg)
            operation.message_post(
                body=_("✅ Opération effectuée par %s") % self.env.user.name
            )

        return True
