# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class TreasuryTransferControl(models.Model):
    _inherit = 'treasury.transfer'

    # =========================================================================
    # CHAMPS POUR LE CONTRÔLE
    # =========================================================================

    control_checked = fields.Boolean(
        string='Contrôle effectué',
        default=False,
        copy=False,
        help="Indique si le contrôle de solde a été effectué"
    )

    control_date = fields.Datetime(
        string='Date du contrôle',
        copy=False,
        readonly=True
    )

    control_user_id = fields.Many2one(
        'res.users',
        string='Contrôlé par',
        copy=False,
        readonly=True
    )

    source_balance_before = fields.Monetary(
        string='Solde source avant',
        currency_field='currency_id',
        copy=False,
        readonly=True
    )

    source_balance_after = fields.Monetary(
        string='Solde source après',
        currency_field='currency_id',
        compute='_compute_balance_after'
    )

    dest_balance_before = fields.Monetary(
        string='Solde destination avant',
        currency_field='currency_id',
        copy=False,
        readonly=True
    )

    dest_balance_after = fields.Monetary(
        string='Solde destination après',
        currency_field='currency_id',
        compute='_compute_balance_after'
    )

    control_warning = fields.Text(
        string='Avertissements',
        compute='_compute_control_warning'
    )

    force_transfer = fields.Boolean(
        string='Forcer le transfert',
        default=False,
        help="Cocher pour forcer le transfert malgré le solde insuffisant "
             "(nécessite les droits de manager)"
    )

    # =========================================================================
    # CALCULS
    # =========================================================================

    @api.depends('amount', 'source_balance_before', 'dest_balance_before')
    def _compute_balance_after(self):
        for transfer in self:
            transfer.source_balance_after = transfer.source_balance_before - transfer.amount
            transfer.dest_balance_after = transfer.dest_balance_before + transfer.amount

    @api.depends('transfer_type', 'amount', 'cash_from_id', 'cash_to_id',
                 'safe_from_id', 'safe_to_id', 'bank_from_id', 'bank_to_id', 'state')
    def _compute_control_warning(self):
        for transfer in self:
            if transfer.state != 'draft':
                transfer.control_warning = False
                continue

            warnings = []
            source_balance, source_name = transfer._get_source_balance()

            if source_balance is not None and transfer.amount > source_balance:
                warnings.append(
                    _("SOLDE INSUFFISANT: %s a un solde de %.2f, "
                      "mais vous tentez de transférer %.2f. "
                      "Manque: %.2f") % (
                        source_name,
                        source_balance,
                        transfer.amount,
                        transfer.amount - source_balance
                    )
                )

            transfer.control_warning = '\n'.join(warnings) if warnings else False

    # =========================================================================
    # MÉTHODES UTILITAIRES
    # =========================================================================

    def _get_source_balance(self):
        """
        Retourne (solde, nom) de la source du transfert.
        Retourne (None, None) si la source n'est pas définie.
        """
        self.ensure_one()

        # Transfert depuis une CAISSE
        if self.transfer_type in ['cash_to_cash', 'cash_to_safe', 'cash_to_bank']:
            if self.cash_from_id:
                # Forcer le recalcul du solde
                self.cash_from_id._compute_current_balance()
                return (self.cash_from_id.current_balance, self.cash_from_id.name)

        # Transfert depuis un COFFRE
        elif self.transfer_type in ['safe_to_cash', 'safe_to_safe', 'safe_to_bank']:
            if self.safe_from_id:
                # Forcer le recalcul du solde
                self.safe_from_id._compute_current_balance()
                return (self.safe_from_id.current_balance, self.safe_from_id.name)

        # Transfert depuis une BANQUE
        elif self.transfer_type in ['bank_to_cash', 'bank_to_safe', 'bank_to_bank']:
            if self.bank_from_id:
                return (self.bank_from_id.current_balance, self.bank_from_id.name)

        return (None, None)

    def _get_destination_balance(self):
        """
        Retourne (solde, nom) de la destination du transfert.
        """
        self.ensure_one()

        if self.transfer_type in ['cash_to_cash', 'safe_to_cash', 'bank_to_cash']:
            if self.cash_to_id:
                return (self.cash_to_id.current_balance, self.cash_to_id.name)

        elif self.transfer_type in ['cash_to_safe', 'safe_to_safe', 'bank_to_safe']:
            if self.safe_to_id:
                return (self.safe_to_id.current_balance, self.safe_to_id.name)

        elif self.transfer_type in ['cash_to_bank', 'safe_to_bank', 'bank_to_bank']:
            if self.bank_to_id:
                return (self.bank_to_id.current_balance, self.bank_to_id.name)

        return (None, None)

    def _is_negative_allowed(self):
        """
        Vérifie si le solde négatif est autorisé pour la source.
        Par défaut: NON autorisé (plus strict).
        """
        self.ensure_one()

        # Transfert depuis une CAISSE
        if self.transfer_type in ['cash_to_cash', 'cash_to_safe', 'cash_to_bank']:
            if self.cash_from_id:
                return getattr(self.cash_from_id, 'allow_negative_balance', False)

        # Transfert depuis un COFFRE
        elif self.transfer_type in ['safe_to_cash', 'safe_to_safe', 'safe_to_bank']:
            if self.safe_from_id:
                return getattr(self.safe_from_id, 'allow_negative_balance', False)

        # Transfert depuis une BANQUE (vérifier le découvert)
        elif self.transfer_type in ['bank_to_cash', 'bank_to_safe', 'bank_to_bank']:
            if self.bank_from_id:
                return getattr(self.bank_from_id, 'allow_negative_balance', True)

        return False

    def _get_overdraft_limit(self):
        """Retourne le découvert autorisé pour les comptes bancaires."""
        self.ensure_one()

        if self.transfer_type in ['bank_to_cash', 'bank_to_safe', 'bank_to_bank']:
            if self.bank_from_id:
                return getattr(self.bank_from_id, 'overdraft_limit', 0) or 0

        return 0

    # =========================================================================
    # CONTRÔLE PRINCIPAL - BLOQUANT
    # =========================================================================

    def _check_balance_before_transfer(self):
        """
        Vérification STRICTE du solde avant transfert.
        Cette méthode lève une erreur si le solde est insuffisant.
        """
        self.ensure_one()

        source_balance, source_name = self._get_source_balance()
        dest_balance, dest_name = self._get_destination_balance()

        _logger.info("="*50)
        _logger.info("CONTRÔLE TRANSFERT: %s", self.name)
        _logger.info("Type: %s", self.transfer_type)
        _logger.info("Source: %s - Solde: %s", source_name, source_balance)
        _logger.info("Destination: %s - Solde: %s", dest_name, dest_balance)
        _logger.info("Montant demandé: %s", self.amount)
        _logger.info("Force transfer: %s", self.force_transfer)
        _logger.info("="*50)

        if source_balance is None:
            raise UserError(_("Impossible de déterminer le solde de la source."))

        # Enregistrer les soldes pour traçabilité
        self.write({
            'source_balance_before': source_balance,
            'dest_balance_before': dest_balance or 0,
            'control_date': fields.Datetime.now(),
            'control_user_id': self.env.user.id,
            'control_checked': True,
        })

        # =====================================================================
        # VÉRIFICATION DU SOLDE INSUFFISANT
        # =====================================================================
        if self.amount > source_balance:
            allow_negative = self._is_negative_allowed()

            # Pour les banques, vérifier le découvert
            if self.transfer_type in ['bank_to_cash', 'bank_to_safe', 'bank_to_bank']:
                overdraft_limit = self._get_overdraft_limit()
                new_balance = source_balance - self.amount

                if new_balance < -overdraft_limit:
                    if not self.force_transfer:
                        raise UserError(
                            _("❌ TRANSFERT REFUSÉ - DÉCOUVERT DÉPASSÉ\n\n"
                              "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                              "Compte bancaire: %s\n"
                              "Solde actuel: %.2f %s\n"
                              "Montant demandé: %.2f %s\n"
                              "Solde après transfert: %.2f %s\n"
                              "Découvert autorisé: %.2f %s\n"
                              "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                              "Le transfert dépasserait le découvert autorisé.\n"
                              "Veuillez réduire le montant ou augmenter le découvert.") % (
                                source_name,
                                source_balance, self.currency_id.symbol,
                                self.amount, self.currency_id.symbol,
                                new_balance, self.currency_id.symbol,
                                overdraft_limit, self.currency_id.symbol
                            )
                        )

            # Pour les caisses et coffres
            elif not allow_negative:
                if not self.force_transfer:
                    raise UserError(
                        _("❌ TRANSFERT REFUSÉ - SOLDE INSUFFISANT\n\n"
                          "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                          "Source: %s\n"
                          "Solde actuel: %.2f %s\n"
                          "Montant demandé: %.2f %s\n"
                          "Manque: %.2f %s\n"
                          "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                          "Le solde de la source est insuffisant pour ce transfert.\n"
                          "Veuillez réduire le montant ou approvisionner la source.") % (
                            source_name,
                            source_balance, self.currency_id.symbol,
                            self.amount, self.currency_id.symbol,
                            self.amount - source_balance, self.currency_id.symbol
                        )
                    )

        # Vérification de la capacité maximum de la destination
        if dest_balance is not None:
            max_capacity = 0

            if self.transfer_type in ['cash_to_cash', 'safe_to_cash', 'bank_to_cash']:
                if self.cash_to_id:
                    max_capacity = getattr(self.cash_to_id, 'max_amount', 0) or 0

            elif self.transfer_type in ['cash_to_safe', 'safe_to_safe', 'bank_to_safe']:
                if self.safe_to_id:
                    max_capacity = getattr(self.safe_to_id, 'max_capacity', 0) or 0

            if max_capacity > 0:
                new_dest_balance = dest_balance + self.amount
                if new_dest_balance > max_capacity:
                    if not self.force_transfer:
                        raise UserError(
                            _("❌ TRANSFERT REFUSÉ - CAPACITÉ DÉPASSÉE\n\n"
                              "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                              "Destination: %s\n"
                              "Solde actuel: %.2f %s\n"
                              "Montant à recevoir: %.2f %s\n"
                              "Solde après transfert: %.2f %s\n"
                              "Capacité maximum: %.2f %s\n"
                              "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                              "Le transfert dépasserait la capacité maximum.") % (
                                dest_name,
                                dest_balance, self.currency_id.symbol,
                                self.amount, self.currency_id.symbol,
                                new_dest_balance, self.currency_id.symbol,
                                max_capacity, self.currency_id.symbol
                            )
                        )

        return True

    # =========================================================================
    # SURCHARGE DE action_confirm - POINT D'ENTRÉE PRINCIPAL
    # =========================================================================

    def action_confirm(self):
        """
        Surcharge de la confirmation pour ajouter le contrôle de solde.
        Le contrôle est effectué AVANT d'appeler la méthode parente.
        """
        for transfer in self:
            if transfer.state != 'draft':
                continue

            # Vérification OBLIGATOIRE du solde
            # Cette méthode lève une erreur si le solde est insuffisant
            transfer._check_balance_before_transfer()

            # Vérifier les droits pour forcer le transfert
            if transfer.force_transfer:
                if not self.env.user.has_group(
                    'adi_treasury_transfer_control.group_transfer_control_manager'
                ):
                    raise UserError(
                        _("Vous n'avez pas les droits pour forcer ce transfert.\n"
                          "Seul un manager peut forcer un transfert avec un solde insuffisant.")
                    )

                # Logger le forçage du transfert
                _logger.warning(
                    "TRANSFERT FORCÉ: %s par %s malgré solde insuffisant",
                    transfer.name, self.env.user.name
                )
                transfer.message_post(
                    body=_("⚠️ Transfert FORCÉ par %s malgré solde insuffisant") % self.env.user.name
                )

        # Appeler la méthode parente
        return super(TreasuryTransferControl, self).action_confirm()

    # =========================================================================
    # MÉTHODES ADDITIONNELLES
    # =========================================================================

    def action_check_transfer(self):
        """Bouton pour vérifier manuellement le transfert."""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_("Le contrôle ne peut être effectué que sur "
                            "les transferts en brouillon."))

        try:
            self._check_balance_before_transfer()

            source_balance, source_name = self._get_source_balance()
            dest_balance, dest_name = self._get_destination_balance()

            self.message_post(
                body=_("✅ Contrôle effectué avec succès<br/>"
                       "• Source: %s (Solde: %.2f)<br/>"
                       "• Destination: %s (Solde: %.2f)<br/>"
                       "• Montant: %.2f") % (
                    source_name, source_balance or 0,
                    dest_name, dest_balance or 0,
                    self.amount
                )
            )

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Contrôle réussi'),
                    'message': _('Le solde est suffisant pour ce transfert.'),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except UserError as e:
            self.control_checked = False
            raise

    def action_reset_control(self):
        """Réinitialiser le contrôle."""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Le contrôle ne peut être réinitialisé que "
                            "pour les transferts en brouillon."))

        self.write({
            'control_checked': False,
            'control_date': False,
            'control_user_id': False,
            'source_balance_before': 0,
            'dest_balance_before': 0,
            'force_transfer': False,
        })

        return True

    @api.model
    def create(self, vals):
        vals['control_checked'] = False
        vals['force_transfer'] = False
        return super(TreasuryTransferControl, self).create(vals)

    def write(self, vals):
        # Réinitialiser le contrôle si le montant ou les sources changent
        reset_fields = ['amount', 'transfer_type', 'cash_from_id', 'cash_to_id',
                       'safe_from_id', 'safe_to_id', 'bank_from_id', 'bank_to_id']

        if any(f in vals for f in reset_fields) and 'control_checked' not in vals:
            vals['control_checked'] = False

        return super(TreasuryTransferControl, self).write(vals)
