# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import AccessError


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
