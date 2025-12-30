# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError


class TreasuryCashOperationDeleteProtection(models.Model):
    """
    Protection contre la suppression des opérations de caisse.
    - Interdit la suppression des opérations dans une clôture validée
    - Interdit la suppression des opérations comptabilisées (il faut d'abord les remettre en brouillon)
    """
    _inherit = 'treasury.cash.operation'

    # Champ pour vérifier si l'opération peut être remise en brouillon
    can_reset_to_draft = fields.Boolean(
        string='Peut être remise en brouillon',
        compute='_compute_can_reset_to_draft',
        store=False
    )

    @api.depends('state', 'closing_id', 'closing_id.state', 'payment_id', 'transfer_id')
    def _compute_can_reset_to_draft(self):
        """Calculer si l'opération peut être remise en brouillon"""
        for operation in self:
            can_reset = (
                operation.state == 'posted' and
                not operation.payment_id and
                not operation.transfer_id and
                (not operation.closing_id or operation.closing_id.state != 'validated')
            )
            operation.can_reset_to_draft = can_reset

    def unlink(self):
        """Vérifier les contraintes avant suppression"""
        for operation in self:
            # Vérifier si l'opération est dans une clôture validée
            if operation.closing_id and operation.closing_id.state == 'validated':
                raise UserError(_(
                    "Impossible de supprimer l'opération '%s' : elle fait partie de la clôture validée '%s'.\n"
                    "Les opérations des clôtures validées ne peuvent pas être supprimées."
                ) % (operation.name, operation.closing_id.name))

            # Vérifier si l'opération est comptabilisée
            if operation.state == 'posted':
                raise UserError(_(
                    "Impossible de supprimer l'opération '%s' : elle est comptabilisée.\n"
                    "Pour supprimer une opération comptabilisée, vous devez d'abord l'annuler "
                    "puis la remettre en brouillon."
                ) % operation.name)

            # Vérifier si l'opération est liée à un transfert
            if operation.transfer_id:
                raise UserError(_(
                    "Impossible de supprimer l'opération '%s' : elle est liée au transfert '%s'.\n"
                    "Pour supprimer cette opération, vous devez annuler le transfert correspondant."
                ) % (operation.name, operation.transfer_id.name))

        return super().unlink()

    def action_open_form(self):
        """Ouvrir le formulaire de l'opération"""
        self.ensure_one()
        return {
            'name': _('Opération de caisse'),
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.cash.operation',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

    def action_reset_to_draft(self):
        """Remettre une opération comptabilisée en brouillon pour permettre sa modification/suppression"""
        for operation in self:
            # Vérifier que l'opération est comptabilisée
            if operation.state != 'posted':
                raise UserError(_(
                    "Seules les opérations comptabilisées peuvent être remises en brouillon."
                ))

            # Vérifier que la clôture n'est pas validée
            if operation.closing_id and operation.closing_id.state == 'validated':
                raise UserError(_(
                    "Impossible de remettre en brouillon l'opération '%s' : "
                    "elle fait partie de la clôture validée '%s'.\n"
                    "Les opérations des clôtures validées sont verrouillées."
                ) % (operation.name, operation.closing_id.name))

            # Vérifier que ce n'est pas une opération de transfert
            if operation.transfer_id:
                raise UserError(_(
                    "Impossible de remettre en brouillon l'opération '%s' : "
                    "elle est liée au transfert '%s'.\n"
                    "Les opérations de transfert ne peuvent pas être modifiées directement."
                ) % (operation.name, operation.transfer_id.name))

            # Vérifier que ce n'est pas une opération liée à un paiement
            if operation.payment_id:
                raise UserError(_(
                    "Impossible de remettre en brouillon l'opération '%s' : "
                    "elle est liée au paiement '%s'.\n"
                    "Les opérations de paiement ne peuvent pas être modifiées directement."
                ) % (operation.name, operation.payment_id.name))

            # Retirer de la clôture si nécessaire
            closing = operation.closing_id
            operation.write({
                'state': 'draft',
                'closing_id': False,
                'is_collected': False,
                'collected_date': False,
                'collected_by': False,
            })

            # Message dans le chatter
            operation.message_post(
                body=_("⚠️ Opération remise en brouillon par %s") % self.env.user.name
            )

            # Rafraîchir la clôture si elle existe
            if closing and closing.state != 'validated':
                closing._compute_totals()
                closing._compute_closing_lines()

        return True


class TreasuryCashAccessProtection(models.Model):
    """
    Protection des champs sensibles sur les caisses.
    Seuls les managers peuvent modifier user_ids et responsible_id.
    """
    _inherit = 'treasury.cash'

    # Champs protégés - seuls les managers peuvent les modifier
    PROTECTED_FIELDS = ['user_ids', 'responsible_id']

    def _is_treasury_manager(self):
        """Vérifier si l'utilisateur est manager de trésorerie"""
        return self.env.user.has_group('adi_treasury.group_treasury_manager')

    def write(self, vals):
        """Vérifier que seuls les managers peuvent modifier les champs protégés"""
        if any(field in vals for field in self.PROTECTED_FIELDS):
            if not self._is_treasury_manager():
                raise AccessError(_(
                    "Vous n'avez pas le droit de modifier les utilisateurs autorisés "
                    "ou le responsable de cette caisse. Seuls les managers peuvent effectuer "
                    "cette opération."
                ))
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """Vérifier les droits à la création si user_ids ou responsible_id sont spécifiés"""
        for vals in vals_list:
            if any(field in vals for field in self.PROTECTED_FIELDS):
                if not self.env.user.has_group('adi_treasury.group_treasury_manager'):
                    raise AccessError(_(
                        "Vous n'avez pas le droit de définir les utilisateurs autorisés "
                        "ou le responsable de cette caisse. Seuls les managers peuvent effectuer "
                        "cette opération."
                    ))
        return super().create(vals_list)


class TreasurySafeAccessProtection(models.Model):
    """
    Protection des champs sensibles sur les coffres.
    Seuls les managers peuvent modifier responsible_ids.
    """
    _inherit = 'treasury.safe'

    # Champs protégés - seuls les managers peuvent les modifier
    PROTECTED_FIELDS = ['responsible_ids']

    def _is_treasury_manager(self):
        """Vérifier si l'utilisateur est manager de trésorerie"""
        return self.env.user.has_group('adi_treasury.group_treasury_manager')

    def write(self, vals):
        """Vérifier que seuls les managers peuvent modifier les champs protégés"""
        if any(field in vals for field in self.PROTECTED_FIELDS):
            if not self._is_treasury_manager():
                raise AccessError(_(
                    "Vous n'avez pas le droit de modifier les responsables de ce coffre. "
                    "Seuls les managers peuvent effectuer cette opération."
                ))
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """Vérifier les droits à la création si responsible_ids est spécifié"""
        for vals in vals_list:
            if any(field in vals for field in self.PROTECTED_FIELDS):
                if not self.env.user.has_group('adi_treasury.group_treasury_manager'):
                    raise AccessError(_(
                        "Vous n'avez pas le droit de définir les responsables de ce coffre. "
                        "Seuls les managers peuvent effectuer cette opération."
                    ))
        return super().create(vals_list)


class TreasuryBankAccessProtection(models.Model):
    """
    Protection des champs sensibles sur les banques.
    Seuls les managers peuvent modifier user_ids et responsible_id.
    """
    _inherit = 'treasury.bank'

    # Champs protégés - seuls les managers peuvent les modifier
    PROTECTED_FIELDS = ['user_ids', 'responsible_id']

    def _is_bank_manager(self):
        """Vérifier si l'utilisateur est manager bancaire ou trésorerie"""
        return (self.env.user.has_group('adi_treasury_bank.group_treasury_bank_manager') or
                self.env.user.has_group('adi_treasury.group_treasury_manager'))

    def write(self, vals):
        """Vérifier que seuls les managers peuvent modifier les champs protégés"""
        if any(field in vals for field in self.PROTECTED_FIELDS):
            if not self._is_bank_manager():
                raise AccessError(_(
                    "Vous n'avez pas le droit de modifier les utilisateurs autorisés "
                    "ou le responsable de ce compte bancaire. Seuls les managers peuvent "
                    "effectuer cette opération."
                ))
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """Vérifier les droits à la création si user_ids ou responsible_id sont spécifiés"""
        for vals in vals_list:
            if any(field in vals for field in self.PROTECTED_FIELDS):
                if not self._is_bank_manager():
                    raise AccessError(_(
                        "Vous n'avez pas le droit de définir les utilisateurs autorisés "
                        "ou le responsable de ce compte bancaire. Seuls les managers peuvent "
                        "effectuer cette opération."
                    ))
        return super().create(vals_list)
