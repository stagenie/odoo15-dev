-- Script pour recréer la vue treasury_dashboard
-- Exécuter avec: psql -d votre_base -f recreate_dashboard_view.sql

DROP VIEW IF EXISTS treasury_dashboard;

CREATE OR REPLACE VIEW treasury_dashboard AS (
    -- Caisses individuelles
    SELECT
        c.id as id,
        COALESCE(c.name, c.code, 'Caisse') as name,
        c.code as code,
        c.current_balance as balance,
        c.currency_id as currency_id,
        'cash'::varchar as type,
        CASE
            WHEN c.current_balance < 0 THEN 1
            WHEN c.current_balance > 0 THEN 10
            ELSE 0
        END as color,
        1 as sequence,
        c.state as state,
        'fa-money'::varchar as icon,
        c.id as res_id,
        'treasury.cash'::varchar as res_model,
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
        'bank'::varchar as type,
        CASE
            WHEN b.current_balance < 0 THEN 1
            WHEN b.current_balance > 0 THEN 4
            ELSE 0
        END as color,
        2 as sequence,
        b.state as state,
        'fa-university'::varchar as icon,
        b.id as res_id,
        'treasury.bank'::varchar as res_model,
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
        s.currency_id as currency_id,
        'safe'::varchar as type,
        CASE
            WHEN s.current_balance < 0 THEN 1
            WHEN s.current_balance > 0 THEN 8
            ELSE 0
        END as color,
        3 as sequence,
        s.state as state,
        'fa-lock'::varchar as icon,
        s.id as res_id,
        'treasury.safe'::varchar as res_model,
        false as has_pending_closing,
        true as is_balance_final
    FROM treasury_safe s
    WHERE s.active = true

    UNION ALL

    -- Total Caisses
    SELECT
        2000001 as id,
        'TOTAL CAISSES'::varchar as name,
        'TOT-CASH'::varchar as code,
        COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) as balance,
        (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
        'total_cash'::varchar as type,
        CASE
            WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) < 0 THEN 1
            WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) > 0 THEN 10
            ELSE 0
        END as color,
        4 as sequence,
        'active'::varchar as state,
        'fa-calculator'::varchar as icon,
        0 as res_id,
        ''::varchar as res_model,
        false as has_pending_closing,
        true as is_balance_final

    UNION ALL

    -- Total Banques
    SELECT
        2000002 as id,
        'TOTAL BANQUES'::varchar as name,
        'TOT-BANK'::varchar as code,
        COALESCE((SELECT SUM(current_balance) FROM treasury_bank WHERE active = true), 0) as balance,
        (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
        'total_bank'::varchar as type,
        CASE
            WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_bank WHERE active = true), 0) < 0 THEN 1
            WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_bank WHERE active = true), 0) > 0 THEN 4
            ELSE 0
        END as color,
        5 as sequence,
        'active'::varchar as state,
        'fa-calculator'::varchar as icon,
        0 as res_id,
        ''::varchar as res_model,
        false as has_pending_closing,
        true as is_balance_final

    UNION ALL

    -- Total Coffres
    SELECT
        2000004 as id,
        'TOTAL COFFRES'::varchar as name,
        'TOT-SAFE'::varchar as code,
        COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) as balance,
        (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
        'total_safe'::varchar as type,
        CASE
            WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) < 0 THEN 1
            WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) > 0 THEN 8
            ELSE 0
        END as color,
        6 as sequence,
        'active'::varchar as state,
        'fa-lock'::varchar as icon,
        0 as res_id,
        ''::varchar as res_model,
        false as has_pending_closing,
        true as is_balance_final

    UNION ALL

    -- Total Général
    SELECT
        2000003 as id,
        'TOTAL GÉNÉRAL'::varchar as name,
        'TOTAL'::varchar as code,
        COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) +
        COALESCE((SELECT SUM(current_balance) FROM treasury_bank WHERE active = true), 0) +
        COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) as balance,
        (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
        'grand_total'::varchar as type,
        CASE
            WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) +
                 COALESCE((SELECT SUM(current_balance) FROM treasury_bank WHERE active = true), 0) +
                 COALESCE((SELECT SUM(current_balance) FROM treasury_safe WHERE active = true), 0) < 0 THEN 1
            ELSE 5
        END as color,
        7 as sequence,
        'active'::varchar as state,
        'fa-balance-scale'::varchar as icon,
        0 as res_id,
        ''::varchar as res_model,
        false as has_pending_closing,
        true as is_balance_final
);

-- Vérification
SELECT 'Vue recréée avec succès!' as message;
SELECT type, COUNT(*) as count FROM treasury_dashboard GROUP BY type ORDER BY type;
SELECT id, name, type, balance, has_pending_closing FROM treasury_dashboard ORDER BY sequence, type;
