# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TreasuryDashboardExtended(models.Model):
    _inherit = 'treasury.dashboard'

    def init(self):
        """Recréer la vue SQL pour inclure les coffres et les totaux étendus"""
        self.env.cr.execute("""
            DROP VIEW IF EXISTS treasury_dashboard;
            CREATE OR REPLACE VIEW treasury_dashboard AS (
                -- Caisses individuelles
                SELECT
                    c.id as id,
                    COALESCE(c.name, c.code, 'Caisse') as name,
                    c.code as code,
                    c.current_balance as balance,
                    c.currency_id as currency_id,
                    'cash' as type,
                    CASE
                        WHEN c.current_balance < 0 THEN 1
                        WHEN c.current_balance > 0 THEN 10
                        ELSE 0
                    END as color,
                    1 as sequence,
                    c.state as state,
                    'fa-money' as icon,
                    c.id as res_id,
                    'treasury.cash' as res_model,
                    EXISTS(
                        SELECT 1 FROM treasury_cash_closing cc
                        WHERE cc.cash_id = c.id AND cc.state IN ('draft', 'confirmed')
                    ) as has_pending_closing,
                    NOT EXISTS(
                        SELECT 1 FROM treasury_cash_closing cc
                        WHERE cc.cash_id = c.id AND cc.state IN ('draft', 'confirmed')
                    ) as is_balance_final
                FROM treasury_cash c
                WHERE c.active = true

                UNION ALL

                -- Banques individuelles
                SELECT
                    1000000 + b.id as id,
                    COALESCE(b.name, b.code, 'Banque') as name,
                    b.code as code,
                    b.current_balance as balance,
                    b.currency_id as currency_id,
                    'bank' as type,
                    CASE
                        WHEN b.current_balance < 0 THEN 1
                        WHEN b.current_balance > 0 THEN 4
                        ELSE 0
                    END as color,
                    2 as sequence,
                    b.state as state,
                    'fa-university' as icon,
                    b.id as res_id,
                    'treasury.bank' as res_model,
                    EXISTS(
                        SELECT 1 FROM treasury_bank_closing bc
                        WHERE bc.bank_id = b.id AND bc.state IN ('draft', 'confirmed')
                    ) as has_pending_closing,
                    NOT EXISTS(
                        SELECT 1 FROM treasury_bank_closing bc
                        WHERE bc.bank_id = b.id AND bc.state IN ('draft', 'confirmed')
                    ) as is_balance_final
                FROM treasury_bank b
                WHERE b.active = true

                UNION ALL

                -- Coffres individuels (pas de clôture, solde toujours finalisé)
                SELECT
                    3000000 + s.id as id,
                    COALESCE(s.name, s.code, 'Coffre') as name,
                    s.code as code,
                    s.current_balance as balance,
                    s.currency_id as currency_id,
                    'safe' as type,
                    CASE
                        WHEN s.current_balance < 0 THEN 1
                        WHEN s.current_balance > 0 THEN 8
                        ELSE 0
                    END as color,
                    3 as sequence,
                    s.state as state,
                    'fa-lock' as icon,
                    s.id as res_id,
                    'treasury.safe' as res_model,
                    false as has_pending_closing,
                    true as is_balance_final
                FROM treasury_safe s
                WHERE s.active = true

                UNION ALL

                -- Total Caisses
                SELECT
                    2000001 as id,
                    'TOTAL CAISSES' as name,
                    'TOT-CASH' as code,
                    COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) as balance,
                    (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
                    'total_cash' as type,
                    CASE
                        WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) < 0 THEN 1
                        WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) > 0 THEN 10
                        ELSE 0
                    END as color,
                    4 as sequence,
                    'active' as state,
                    'fa-calculator' as icon,
                    0 as res_id,
                    '' as res_model,
                    false as has_pending_closing,
                    true as is_balance_final

                UNION ALL

                -- Total Banques
                SELECT
                    2000002 as id,
                    'TOTAL BANQUES' as name,
                    'TOT-BANK' as code,
                    COALESCE((SELECT SUM(current_balance) FROM treasury_bank WHERE active = true), 0) as balance,
                    (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
                    'total_bank' as type,
                    CASE
                        WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_bank WHERE active = true), 0) < 0 THEN 1
                        WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_bank WHERE active = true), 0) > 0 THEN 4
                        ELSE 0
                    END as color,
                    5 as sequence,
                    'active' as state,
                    'fa-calculator' as icon,
                    0 as res_id,
                    '' as res_model,
                    false as has_pending_closing,
                    true as is_balance_final

                UNION ALL

                -- Total Coffres
                SELECT
                    2000004 as id,
                    'TOTAL COFFRES' as name,
                    'TOT-SAFE' as code,
                    COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) as balance,
                    (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
                    'total_safe' as type,
                    CASE
                        WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) < 0 THEN 1
                        WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) > 0 THEN 8
                        ELSE 0
                    END as color,
                    6 as sequence,
                    'active' as state,
                    'fa-lock' as icon,
                    0 as res_id,
                    '' as res_model,
                    false as has_pending_closing,
                    true as is_balance_final

                UNION ALL

                -- Total Général (Caisses + Banques + Coffres)
                SELECT
                    2000003 as id,
                    'TOTAL GÉNÉRAL' as name,
                    'TOTAL' as code,
                    COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) +
                    COALESCE((SELECT SUM(current_balance) FROM treasury_bank WHERE active = true), 0) +
                    COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) as balance,
                    (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
                    'grand_total' as type,
                    CASE
                        WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) +
                             COALESCE((SELECT SUM(current_balance) FROM treasury_bank WHERE active = true), 0) +
                             COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) < 0 THEN 1
                        ELSE 5
                    END as color,
                    7 as sequence,
                    'active' as state,
                    'fa-balance-scale' as icon,
                    0 as res_id,
                    '' as res_model,
                    false as has_pending_closing,
                    true as is_balance_final
            )
        """)

    @api.model
    def get_dashboard_data(self):
        """Récupérer toutes les données du tableau de bord (avec coffres)"""
        company = self.env.company
        currency = company.currency_id

        # Récupérer les caisses
        cashes = self.env['treasury.cash'].search([
            ('company_id', '=', company.id),
            ('active', '=', True)
        ])

        cash_data = []
        total_cash = 0.0
        for cash in cashes:
            cash_data.append({
                'id': cash.id,
                'name': cash.name,
                'code': cash.code,
                'balance': cash.current_balance,
                'currency_id': cash.currency_id.id,
                'currency_symbol': cash.currency_id.symbol,
                'state': cash.state,
                'type': 'cash',
                'color': 'danger' if cash.current_balance < 0 else ('success' if cash.current_balance > 0 else 'secondary'),
            })
            total_cash += cash.current_balance

        # Récupérer les banques
        banks = self.env['treasury.bank'].search([
            ('company_id', '=', company.id),
            ('active', '=', True)
        ])

        bank_data = []
        total_bank = 0.0
        for bank in banks:
            bank_data.append({
                'id': bank.id,
                'name': bank.name,
                'code': bank.code,
                'balance': bank.current_balance,
                'available_balance': bank.available_balance,
                'currency_id': bank.currency_id.id,
                'currency_symbol': bank.currency_id.symbol,
                'state': bank.state,
                'type': 'bank',
                'bank_name': bank.bank_name or '',
                'color': 'danger' if bank.current_balance < 0 else ('primary' if bank.current_balance > 0 else 'secondary'),
            })
            total_bank += bank.current_balance

        # Récupérer les coffres
        safes = self.env['treasury.safe'].search([
            ('company_id', '=', company.id),
            ('active', '=', True)
        ])

        safe_data = []
        total_safe = 0.0
        for safe in safes:
            safe_data.append({
                'id': safe.id,
                'name': safe.name,
                'code': safe.code,
                'balance': safe.current_balance,
                'currency_id': safe.currency_id.id,
                'currency_symbol': safe.currency_id.symbol,
                'state': safe.state,
                'type': 'safe',
                'location': safe.location or '',
                'color': 'danger' if safe.current_balance < 0 else ('purple' if safe.current_balance > 0 else 'secondary'),
            })
            total_safe += safe.current_balance

        grand_total = total_cash + total_bank + total_safe

        return {
            'cashes': cash_data,
            'banks': bank_data,
            'safes': safe_data,
            'total_cash': total_cash,
            'total_bank': total_bank,
            'total_safe': total_safe,
            'grand_total': grand_total,
            'currency_symbol': currency.symbol,
            'currency_id': currency.id,
        }
