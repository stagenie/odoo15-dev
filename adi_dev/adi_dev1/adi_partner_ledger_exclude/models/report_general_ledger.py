# -*- coding: utf-8 -*-

from odoo import api, models


class ReportGeneralLedger(models.AbstractModel):
    _inherit = 'report.accounting_pdf_reports.report_general_ledger'

    def _get_account_move_entry(self, accounts, analytic_account_ids, partner_ids,
                                init_balance, sortby, display_account):
        """
        Hérite de la méthode _get_account_move_entry pour :
        - Exclure les factures marquées comme 'exclude_from_partner_ledger'
        - Filtrer par état du mouvement (posted uniquement par défaut, ou selon target_move)
        """
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = {x: [] for x in accounts.ids}

        # Clause d'exclusion pour les factures marquées
        exclude_clause = ' AND (m.exclude_from_partner_ledger IS NULL OR m.exclude_from_partner_ledger = FALSE) '

        # Clause de filtrage par état du mouvement
        # Par défaut, on n'affiche que les écritures validées (posted)
        # Sauf si target_move = 'all', auquel cas on inclut aussi les brouillons
        # Note: target_move est converti en 'state' dans le contexte par _build_contexts()
        target_move = self.env.context.get('state', 'posted')
        if target_move == 'posted':
            state_clause = " AND m.state = 'posted' "
        else:
            # 'all' = draft + posted (jamais les cancel)
            state_clause = " AND m.state IN ('draft', 'posted') "

        # Prepare initial sql query and Get the initial move lines
        if init_balance:
            context = dict(self.env.context)
            context['date_from'] = self.env.context.get('date_from')
            context['date_to'] = False
            context['initial_bal'] = True
            if analytic_account_ids:
                context['analytic_account_ids'] = analytic_account_ids
            if partner_ids:
                context['partner_ids'] = partner_ids
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(context)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

            # SQL modifié avec clause d'exclusion et filtre d'état
            sql = ("""SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode,
                   0.0 AS amount_currency, '' AS lref, 'Initial Balance' AS lname,
                   COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit,
                   COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance,
                   '' AS lpartner_id, '' AS move_name, '' AS mmove_id, '' AS currency_code,
                   NULL AS currency_id, '' AS invoice_id, '' AS invoice_type,
                   '' AS invoice_number, '' AS partner_name
                   FROM account_move_line l
                   LEFT JOIN account_move m ON (l.move_id=m.id)
                   LEFT JOIN res_currency c ON (l.currency_id=c.id)
                   LEFT JOIN res_partner p ON (l.partner_id=p.id)
                   JOIN account_journal j ON (l.journal_id=j.id)
                   WHERE l.account_id IN %s""" + filters + exclude_clause + state_clause + ' GROUP BY l.account_id')

            params = (tuple(accounts.ids),) + tuple(init_where_params)
            cr.execute(sql, params)
            for row in cr.dictfetchall():
                move_lines[row.pop('account_id')].append(row)

        sql_sort = 'l.date, l.move_id'
        if sortby == 'sort_journal_partner':
            sql_sort = 'j.code, p.name, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        context = dict(self.env.context)
        if analytic_account_ids:
            context['analytic_account_ids'] = analytic_account_ids
        if partner_ids:
            context['partner_ids'] = partner_ids
        tables, where_clause, where_params = MoveLine.with_context(context)._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines
        # SQL modifié avec clause d'exclusion et filtre d'état
        sql = ('''SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate,
            j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref,
            l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit,
            COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,
            m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name
            FROM account_move_line l
            JOIN account_move m ON (l.move_id=m.id)
            LEFT JOIN res_currency c ON (l.currency_id=c.id)
            LEFT JOIN res_partner p ON (l.partner_id=p.id)
            JOIN account_journal j ON (l.journal_id=j.id)
            JOIN account_account acc ON (l.account_id = acc.id)
            WHERE l.account_id IN %s ''' + filters + exclude_clause + state_clause +
            ''' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency,
            l.ref, l.name, m.name, c.symbol, p.name ORDER BY ''' + sql_sort)

        params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                balance += line['debit'] - line['credit']
            row['balance'] += balance
            move_lines[row.pop('account_id')].append(row)

        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in accounts:
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                res['debit'] += line['debit']
                res['credit'] += line['credit']
                res['balance'] = line['balance']
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)

        return account_res