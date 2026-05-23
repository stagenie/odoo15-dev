# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class TreasuryBalanceFixWizard(models.TransientModel):
    _name = 'treasury.balance.fix.wizard'
    _description = "Wizard de réparation des soldes initiaux clôtures"

    cash_id = fields.Many2one(
        'treasury.cash',
        string='Caisse (vide = toutes)',
        help="Si vide, analyse toutes les caisses"
    )

    date_from = fields.Date(
        string='Depuis',
        help="Limiter l'analyse aux clôtures depuis cette date"
    )

    dry_run = fields.Boolean(
        string='Simulation (dry-run)',
        default=True,
        help="Si coché, identifie les anomalies sans les corriger"
    )

    fix_duplicates = fields.Boolean(
        string='Renuméroter les doublons',
        default=False,
        help="Si plusieurs clôtures ont le même closing_number pour le même jour, "
             "renuméroter selon l'ordre des IDs"
    )

    result_log = fields.Text(
        string='Résultat',
        readonly=True
    )

    def action_analyze_and_fix(self):
        """Identifier + (optionnel) corriger les anomalies de balance_start."""
        self.ensure_one()

        Closing = self.env['treasury.cash.closing']

        domain = [('state', '=', 'validated')]
        if self.cash_id:
            domain.append(('cash_id', '=', self.cash_id.id))
        if self.date_from:
            domain.append(('closing_date', '>=', self.date_from))

        # Toutes les clôtures validées triées chronologiquement par caisse
        closings = Closing.search(
            domain,
            order='cash_id, closing_date, closing_number, id'
        )

        anomalies = []
        duplicates_fixed = 0

        # 1) Détecter doublons closing_number
        cash_date_map = {}
        for c in closings:
            key = (c.cash_id.id, c.closing_date)
            cash_date_map.setdefault(key, []).append(c)

        if self.fix_duplicates and not self.dry_run:
            for (cash_id, date), group in cash_date_map.items():
                # Trier par id et renuméroter séquentiellement
                group_sorted = sorted(group, key=lambda x: x.id)
                for idx, c in enumerate(group_sorted, 1):
                    if c.closing_number != idx:
                        old_num = c.closing_number
                        c.with_context(skip_compute=True).write({'closing_number': idx})
                        duplicates_fixed += 1
                        _logger.info(
                            "[BALANCE_FIX] Renumérotation %s: #%s → #%s",
                            c.name, old_num, idx
                        )

        # 2) Détecter anomalies balance_start
        # Re-trier après éventuelle renumérotation
        if self.fix_duplicates and not self.dry_run:
            closings = Closing.search(domain, order='cash_id, closing_date, closing_number, id')

        # Chainage par caisse: balance_start de N+1 doit = balance_end_real de N
        prev_by_cash = {}
        for c in closings:
            prev = prev_by_cash.get(c.cash_id.id)
            if prev is not None:
                expected = prev.balance_end_real
                if abs(c.balance_start - expected) > 0.01:
                    anomalies.append({
                        'closing': c,
                        'prev': prev,
                        'current_start': c.balance_start,
                        'expected_start': expected,
                    })
            prev_by_cash[c.cash_id.id] = c

        # 3) Réparation (si pas dry-run)
        fixed_count = 0
        if not self.dry_run:
            for anom in anomalies:
                anom['closing'].with_context(skip_compute=True).write({
                    'balance_start': anom['expected_start'],
                })
                anom['closing'].message_post(body=_(
                    "🔧 Solde initial corrigé par wizard de réparation.<br/>"
                    "Ancien: %s → Nouveau: %s (de %s)"
                ) % (
                    anom['current_start'],
                    anom['expected_start'],
                    anom['prev'].name,
                ))
                fixed_count += 1
                _logger.info(
                    "[BALANCE_FIX] Réparé %s: balance_start %s → %s",
                    anom['closing'].name,
                    anom['current_start'],
                    anom['expected_start'],
                )

        # 4) Compiler le rapport
        lines = []
        lines.append("=" * 70)
        lines.append("RAPPORT D'ANALYSE - SOLDES INITIAUX CLÔTURES")
        lines.append("=" * 70)
        lines.append(f"Mode: {'SIMULATION (dry-run)' if self.dry_run else 'RÉPARATION ACTIVE'}")
        lines.append(f"Clôtures analysées: {len(closings)}")
        lines.append(f"Doublons closing_number renumérotés: {duplicates_fixed}")
        lines.append(f"Anomalies balance_start détectées: {len(anomalies)}")
        if not self.dry_run:
            lines.append(f"Anomalies corrigées: {fixed_count}")
        lines.append("")

        if anomalies:
            lines.append("ANOMALIES DÉTECTÉES:")
            lines.append("-" * 70)
            for anom in anomalies:
                c = anom['closing']
                lines.append(
                    f"  {c.name} (id={c.id}, caisse={c.cash_id.name})"
                )
                lines.append(
                    f"    balance_start actuel : {anom['current_start']:>15,.2f}"
                )
                lines.append(
                    f"    balance_start attendu: {anom['expected_start']:>15,.2f} "
                    f"(de {anom['prev'].name})"
                )
                lines.append(
                    f"    écart                : {anom['current_start'] - anom['expected_start']:>15,.2f}"
                )
                lines.append("")
        else:
            lines.append("✅ Aucune anomalie détectée.")

        self.result_log = "\n".join(lines)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.balance.fix.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }
