# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class TreasuryDashboard(models.Model):
    _name = 'treasury.dashboard'
    _description = 'Tableau de Bord Trésorerie'
    _auto = False  # Pas de table en base

    name = fields.Char(string='Nom')
    code = fields.Char(string='Code')
    balance = fields.Monetary(string='Solde', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Devise')
    type = fields.Selection([
        ('cash', 'Caisse'),
        ('bank', 'Banque'),
        ('total_cash', 'Total Caisses'),
        ('total_bank', 'Total Banques'),
        ('grand_total', 'Total Général'),
    ], string='Type')
    color = fields.Integer(string='Couleur')
    sequence = fields.Integer(string='Séquence')
    state = fields.Selection([
        ('open', 'Ouvert'),
        ('active', 'Actif'),
        ('closed', 'Fermé'),
    ], string='État')
    icon = fields.Char(string='Icône')
    res_id = fields.Integer(string='ID Source')
    res_model = fields.Char(string='Modèle Source')

    def init(self):
        """Créer la vue SQL pour le tableau de bord"""
        self.env.cr.execute("""
            DROP VIEW IF EXISTS treasury_dashboard;
            CREATE OR REPLACE VIEW treasury_dashboard AS (
                -- Caisses
                SELECT
                    c.id as id,
                    c.name as name,
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
                    'treasury.cash' as res_model
                FROM treasury_cash c
                WHERE c.active = true

                UNION ALL

                -- Banques
                SELECT
                    1000000 + b.id as id,
                    b.name as name,
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
                    'treasury.bank' as res_model
                FROM treasury_bank b
                WHERE b.active = true

                UNION ALL

                -- Total Caisses
                SELECT
                    2000001 as id,
                    'TOTAL CAISSES' as name,
                    'TOT-CASH' as code,
                    COALESCE(SUM(c.current_balance), 0) as balance,
                    (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
                    'total_cash' as type,
                    CASE
                        WHEN COALESCE(SUM(c.current_balance), 0) < 0 THEN 1
                        WHEN COALESCE(SUM(c.current_balance), 0) > 0 THEN 10
                        ELSE 0
                    END as color,
                    3 as sequence,
                    'active' as state,
                    'fa-calculator' as icon,
                    0 as res_id,
                    '' as res_model
                FROM treasury_cash c
                WHERE c.active = true

                UNION ALL

                -- Total Banques
                SELECT
                    2000002 as id,
                    'TOTAL BANQUES' as name,
                    'TOT-BANK' as code,
                    COALESCE(SUM(b.current_balance), 0) as balance,
                    (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
                    'total_bank' as type,
                    CASE
                        WHEN COALESCE(SUM(b.current_balance), 0) < 0 THEN 1
                        WHEN COALESCE(SUM(b.current_balance), 0) > 0 THEN 4
                        ELSE 0
                    END as color,
                    4 as sequence,
                    'active' as state,
                    'fa-calculator' as icon,
                    0 as res_id,
                    '' as res_model
                FROM treasury_bank b
                WHERE b.active = true

                UNION ALL

                -- Total Général
                SELECT
                    2000003 as id,
                    'TOTAL GÉNÉRAL' as name,
                    'TOTAL' as code,
                    COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) +
                    COALESCE((SELECT SUM(current_balance) FROM treasury_bank WHERE active = true), 0) as balance,
                    (SELECT id FROM res_currency WHERE name = 'XOF' LIMIT 1) as currency_id,
                    'grand_total' as type,
                    CASE
                        WHEN COALESCE((SELECT SUM(current_balance) FROM treasury_cash WHERE active = true), 0) +
                             COALESCE((SELECT SUM(current_balance) FROM treasury_bank WHERE active = true), 0) < 0 THEN 1
                        ELSE 5
                    END as color,
                    5 as sequence,
                    'active' as state,
                    'fa-balance-scale' as icon,
                    0 as res_id,
                    '' as res_model
            )
        """)

    @api.model
    def get_dashboard_data(self):
        """Récupérer toutes les données du tableau de bord"""
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

        grand_total = total_cash + total_bank

        return {
            'cashes': cash_data,
            'banks': bank_data,
            'total_cash': total_cash,
            'total_bank': total_bank,
            'grand_total': grand_total,
            'currency_symbol': currency.symbol,
            'currency_id': currency.id,
        }

    def action_open_record(self):
        """Ouvrir l'enregistrement source"""
        self.ensure_one()
        if self.res_model and self.res_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': self.res_model,
                'res_id': self.res_id,
                'view_mode': 'form',
                'target': 'current',
            }
