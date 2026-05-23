# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class TreasuryCashClosing(models.Model):
    _inherit = 'treasury.cash.closing'

    @api.depends('cash_id', 'closing_number', 'closing_date', 'period_start', 'state')
    def _compute_balance_start(self):
        """Override: recherche robuste de la dernière clôture validée.

        Corrige bug intermittent où balance_start ne reprenait pas
        balance_end_real de la dernière clôture validée chronologiquement
        lorsque plusieurs clôtures existaient pour la même journée.

        Améliorations vs version de base:
        - Tiebreaker 'id desc' dans le order pour ordre déterministe
        - Exclusion explicite de soi-même via ('id', '!=', self.id)
        - Fallback vers cash.last_closing_balance si search ne trouve rien
        - Logs diagnostic [BALANCE_FIX] pour traçabilité
        """
        for closing in self:
            if not closing.cash_id:
                closing.balance_start = 0.0
                continue

            current_id = closing.id if isinstance(closing.id, int) else 0

            # Pour record non-sauvegardé, closing_number est encore la valeur par
            # défaut (1) et ne reflète pas le numéro réel qui sera attribué.
            # On calcule le numéro effectif pour que la recherche couvre toutes
            # les clôtures déjà validées du même jour.
            if not current_id and closing.cash_id and closing.closing_date:
                existing_today = self.sudo().search_count([
                    ('cash_id', '=', closing.cash_id.id),
                    ('closing_date', '=', closing.closing_date),
                ])
                effective_number = existing_today + 1
            else:
                effective_number = closing.closing_number

            last_closing = self.sudo().search([
                ('cash_id', '=', closing.cash_id.id),
                ('state', '=', 'validated'),
                ('id', '!=', current_id),
                '|',
                ('closing_date', '<', closing.closing_date),
                '&',
                ('closing_date', '=', closing.closing_date),
                ('closing_number', '<', effective_number),
            ], order='closing_date desc, closing_number desc, id desc', limit=1)

            if last_closing:
                new_balance = last_closing.balance_end_real
                _logger.info(
                    "[BALANCE_FIX] Closing %s (id=%s): balance_start=%s "
                    "reprise de %s (id=%s, real=%s)",
                    closing.name or 'NEW', current_id, new_balance,
                    last_closing.name, last_closing.id, last_closing.balance_end_real
                )
                closing.balance_start = new_balance
            elif closing.cash_id.last_closing_balance:
                # Fallback: utiliser dernier solde mémorisé sur la caisse
                closing.balance_start = closing.cash_id.last_closing_balance
                _logger.info(
                    "[BALANCE_FIX] Closing %s (id=%s): balance_start=%s "
                    "fallback depuis cash.last_closing_balance",
                    closing.name or 'NEW', current_id,
                    closing.cash_id.last_closing_balance
                )
            else:
                # Aucune clôture précédente: somme opérations historiques
                balance = 0.0
                if closing.period_start:
                    previous_operations = self.env['treasury.cash.operation'].search([
                        ('cash_id', '=', closing.cash_id.id),
                        ('state', '=', 'posted'),
                        ('date', '<', closing.period_start),
                    ])
                    for op in previous_operations:
                        if op.operation_type == 'in':
                            balance += op.amount
                        else:
                            balance -= op.amount
                closing.balance_start = balance
                _logger.info(
                    "[BALANCE_FIX] Closing %s (id=%s): balance_start=%s "
                    "calculé depuis opérations historiques",
                    closing.name or 'NEW', current_id, balance
                )

    @api.model_create_multi
    def create(self, vals_list):
        closings = super().create(vals_list)
        # Forcer recalcul après création complète (anti-stale cache)
        closings.invalidate_cache(['balance_start', 'balance_end_theoretical'])
        for closing in closings:
            closing._compute_balance_start()
            closing._compute_theoretical_balance()
            if closing.state == 'draft' and not closing.balance_end_real_manual:
                closing.balance_end_real = closing.balance_end_theoretical
        return closings
