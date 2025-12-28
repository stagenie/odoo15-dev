# -*- coding: utf-8 -*-
"""
Extension du tableau de bord pour afficher les soldes rapprochés et non rapprochés.

Ce module ajoute :
- Champs reconciled_balance et unreconciled_balance sur treasury.dashboard
- Lignes de totaux pour les soldes rapprochés/non rapprochés des banques
- Totaux généraux avec perspective rapprochée/non rapprochée

Option B : Le rapprochement concerne uniquement les banques.
- Total Banques Rapproché = Somme des reconciled_balance des banques
- Total Banques Non Rapproché = Somme des unreconciled_balance des banques
- Total Général Rapproché = Caisses + Coffres + Banques Rapprochées
- Total Général Non Rapproché = Caisses + Coffres + Banques Non Rapprochées
"""

from odoo import models, fields, api


class TreasuryDashboardReconciled(models.Model):
    _inherit = 'treasury.dashboard'

    # Extension du champ type pour les nouveaux types de totaux
    type = fields.Selection(
        selection_add=[
            ('total_bank_reconciled', 'Total Banques Rapproché'),
            ('total_bank_unreconciled', 'Total Banques Non Rapproché'),
            ('grand_total_reconciled', 'Total Général Rapproché'),
            ('grand_total_unreconciled', 'Total Général Non Rapproché'),
        ]
    )

    # Nouveaux champs pour les soldes rapprochés
    reconciled_balance = fields.Monetary(
        string='Solde Rapproché',
        currency_field='currency_id'
    )
    unreconciled_balance = fields.Monetary(
        string='Solde Non Rapproché',
        currency_field='currency_id'
    )

    def init(self):
        """
        Surcharge de la vue SQL pour inclure les soldes rapprochés.

        Nouveaux types ajoutés :
        - total_bank_reconciled : Total des soldes rapprochés des banques
        - total_bank_unreconciled : Total des soldes non rapprochés des banques
        - grand_total_reconciled : Total général avec banques rapprochées
        - grand_total_unreconciled : Total général avec banques non rapprochées
        """
        self.env.cr.execute("""
            DROP VIEW IF EXISTS treasury_dashboard;
            CREATE OR REPLACE VIEW treasury_dashboard AS (
                -- Caisses individuelles
                SELECT
                    c.id as id,
                    COALESCE(c.name, c.code, 'Caisse') as name,
                    c.code as code,
                    c.current_balance as balance,
                    0.0 as reconciled_balance,
                    0.0 as unreconciled_balance,
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

                -- Banques individuelles (avec soldes rapprochés)
                SELECT
                    1000000 + b.id as id,
                    COALESCE(b.name, b.code, 'Banque') as name,
                    b.code as code,
                    b.current_balance as balance,
                    COALESCE(b.reconciled_balance, 0.0) as reconciled_balance,
                    COALESCE(b.unreconciled_balance, 0.0) as unreconciled_balance,
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

                -- Coffres individuels
                SELECT
                    3000000 + s.id as id,
                    COALESCE(s.name, s.code, 'Coffre') as name,
                    s.code as code,
                    s.current_balance as balance,
                    0.0 as reconciled_balance,
                    0.0 as unreconciled_balance,
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
                    0.0 as reconciled_balance,
                    0.0 as unreconciled_balance,
                    (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
                    'total_cash' as type,
                    CASE
                        WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) < 0 THEN 1
                        WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) > 0 THEN 10
                        ELSE 0
                    END as color,
                    10 as sequence,
                    'active' as state,
                    'fa-calculator' as icon,
                    0 as res_id,
                    '' as res_model,
                    false as has_pending_closing,
                    true as is_balance_final

                UNION ALL

                -- Total Banques (Actuel)
                SELECT
                    2000002 as id,
                    'TOTAL BANQUES' as name,
                    'TOT-BANK' as code,
                    COALESCE((SELECT SUM(current_balance) FROM treasury_bank WHERE active = true), 0) as balance,
                    COALESCE((SELECT SUM(reconciled_balance) FROM treasury_bank WHERE active = true), 0) as reconciled_balance,
                    COALESCE((SELECT SUM(unreconciled_balance) FROM treasury_bank WHERE active = true), 0) as unreconciled_balance,
                    (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
                    'total_bank' as type,
                    CASE
                        WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_bank WHERE active = true), 0) < 0 THEN 1
                        WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_bank WHERE active = true), 0) > 0 THEN 4
                        ELSE 0
                    END as color,
                    11 as sequence,
                    'active' as state,
                    'fa-calculator' as icon,
                    0 as res_id,
                    '' as res_model,
                    false as has_pending_closing,
                    true as is_balance_final

                UNION ALL

                -- Total Banques Rapproché
                SELECT
                    2000012 as id,
                    'TOTAL BANQUES RAPPROCHÉ' as name,
                    'TOT-BANK-REC' as code,
                    COALESCE((SELECT SUM(reconciled_balance) FROM treasury_bank WHERE active = true), 0) as balance,
                    COALESCE((SELECT SUM(reconciled_balance) FROM treasury_bank WHERE active = true), 0) as reconciled_balance,
                    0.0 as unreconciled_balance,
                    (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
                    'total_bank_reconciled' as type,
                    CASE
                        WHEN COALESCE((SELECT SUM(reconciled_balance) FROM treasury_bank WHERE active = true), 0) < 0 THEN 1
                        WHEN COALESCE((SELECT SUM(reconciled_balance) FROM treasury_bank WHERE active = true), 0) > 0 THEN 10
                        ELSE 0
                    END as color,
                    12 as sequence,
                    'active' as state,
                    'fa-check-circle' as icon,
                    0 as res_id,
                    '' as res_model,
                    false as has_pending_closing,
                    true as is_balance_final

                UNION ALL

                -- Total Banques Non Rapproché
                SELECT
                    2000013 as id,
                    'TOTAL BANQUES NON RAPPROCHÉ' as name,
                    'TOT-BANK-UNREC' as code,
                    COALESCE((SELECT SUM(unreconciled_balance) FROM treasury_bank WHERE active = true), 0) as balance,
                    0.0 as reconciled_balance,
                    COALESCE((SELECT SUM(unreconciled_balance) FROM treasury_bank WHERE active = true), 0) as unreconciled_balance,
                    (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
                    'total_bank_unreconciled' as type,
                    CASE
                        WHEN COALESCE((SELECT SUM(unreconciled_balance) FROM treasury_bank WHERE active = true), 0) < 0 THEN 1
                        WHEN COALESCE((SELECT SUM(unreconciled_balance) FROM treasury_bank WHERE active = true), 0) > 0 THEN 3
                        ELSE 0
                    END as color,
                    13 as sequence,
                    'active' as state,
                    'fa-clock-o' as icon,
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
                    0.0 as reconciled_balance,
                    0.0 as unreconciled_balance,
                    (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
                    'total_safe' as type,
                    CASE
                        WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) < 0 THEN 1
                        WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) > 0 THEN 8
                        ELSE 0
                    END as color,
                    14 as sequence,
                    'active' as state,
                    'fa-lock' as icon,
                    0 as res_id,
                    '' as res_model,
                    false as has_pending_closing,
                    true as is_balance_final

                UNION ALL

                -- Total Général (Actuel)
                SELECT
                    2000003 as id,
                    'TOTAL GÉNÉRAL' as name,
                    'TOTAL' as code,
                    COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) +
                    COALESCE((SELECT SUM(current_balance) FROM treasury_bank WHERE active = true), 0) +
                    COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) as balance,
                    0.0 as reconciled_balance,
                    0.0 as unreconciled_balance,
                    (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
                    'grand_total' as type,
                    CASE
                        WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) +
                             COALESCE((SELECT SUM(current_balance) FROM treasury_bank WHERE active = true), 0) +
                             COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) < 0 THEN 1
                        ELSE 5
                    END as color,
                    20 as sequence,
                    'active' as state,
                    'fa-balance-scale' as icon,
                    0 as res_id,
                    '' as res_model,
                    false as has_pending_closing,
                    true as is_balance_final

                UNION ALL

                -- Total Général Rapproché (Caisses + Coffres + Banques Rapprochées)
                SELECT
                    2000023 as id,
                    'TOTAL GÉNÉRAL (Rapproché)' as name,
                    'TOTAL-REC' as code,
                    COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) +
                    COALESCE((SELECT SUM(reconciled_balance) FROM treasury_bank WHERE active = true), 0) +
                    COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) as balance,
                    COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) +
                    COALESCE((SELECT SUM(reconciled_balance) FROM treasury_bank WHERE active = true), 0) +
                    COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) as reconciled_balance,
                    0.0 as unreconciled_balance,
                    (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
                    'grand_total_reconciled' as type,
                    CASE
                        WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) +
                             COALESCE((SELECT SUM(reconciled_balance) FROM treasury_bank WHERE active = true), 0) +
                             COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) < 0 THEN 1
                        ELSE 10
                    END as color,
                    21 as sequence,
                    'active' as state,
                    'fa-check-circle' as icon,
                    0 as res_id,
                    '' as res_model,
                    false as has_pending_closing,
                    true as is_balance_final

                UNION ALL

                -- Total Général Non Rapproché (Caisses + Coffres + Banques Non Rapprochées)
                SELECT
                    2000024 as id,
                    'TOTAL GÉNÉRAL (Non Rapproché)' as name,
                    'TOTAL-UNREC' as code,
                    COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) +
                    COALESCE((SELECT SUM(unreconciled_balance) FROM treasury_bank WHERE active = true), 0) +
                    COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) as balance,
                    0.0 as reconciled_balance,
                    COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) +
                    COALESCE((SELECT SUM(unreconciled_balance) FROM treasury_bank WHERE active = true), 0) +
                    COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) as unreconciled_balance,
                    (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
                    'grand_total_unreconciled' as type,
                    CASE
                        WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) +
                             COALESCE((SELECT SUM(unreconciled_balance) FROM treasury_bank WHERE active = true), 0) +
                             COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) < 0 THEN 1
                        ELSE 3
                    END as color,
                    22 as sequence,
                    'active' as state,
                    'fa-clock-o' as icon,
                    0 as res_id,
                    '' as res_model,
                    false as has_pending_closing,
                    true as is_balance_final
            )
        """)

    @api.model
    def get_show_reconciliation(self):
        """Retourne si l'affichage des détails de rapprochement est activé"""
        return self.env['treasury.config.reconciliation'].get_show_reconciliation_details()
