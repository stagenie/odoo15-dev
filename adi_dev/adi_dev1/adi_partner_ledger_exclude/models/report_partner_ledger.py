# -*- coding: utf-8 -*-

from odoo import api, models


class ReportPartnerLedger(models.AbstractModel):
    _inherit = 'report.accounting_pdf_reports.report_partnerledger'

    def _lines(self, data, partner):
        """
        Hérite de la méthode _lines pour exclure les factures marquées
        comme 'exclude_from_partner_ledger'
        """
        full_account = []
        currency = self.env['res.currency']
        query_get_data = self.env['account.move.line'].with_context(
            data['form'].get('used_context', {})
        )._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else \
            ' AND "account_move_line".full_reconcile_id IS NULL '

        # Clause d'exclusion pour les factures marquées
        exclude_clause = ' AND (m.exclude_from_partner_ledger IS NULL OR m.exclude_from_partner_ledger = FALSE) '

        params = [
            partner.id,
            tuple(data['computed']['move_state']),
            tuple(data['computed']['account_ids'])
        ] + query_get_data[2]

        query = """
            SELECT "account_move_line".id, "account_move_line".date, j.code,
                   acc.code as a_code, acc.name as a_name, "account_move_line".ref,
                   m.name as move_name, "account_move_line".name,
                   "account_move_line".debit, "account_move_line".credit,
                   "account_move_line".amount_currency, "account_move_line".currency_id,
                   c.symbol AS currency_code
            FROM """ + query_get_data[0] + """
            LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
            LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
            LEFT JOIN res_currency c ON ("account_move_line".currency_id = c.id)
            LEFT JOIN account_move m ON (m.id = "account_move_line".move_id)
            WHERE "account_move_line".partner_id = %s
                AND m.state IN %s
                AND "account_move_line".account_id IN %s
                AND """ + query_get_data[1] + reconcile_clause + exclude_clause + """
                ORDER BY "account_move_line".date"""

        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        sum = 0.0
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format

        for r in res:
            r['date'] = r['date']
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('move_name', 'ref', 'name')
                if r[field_name] not in (None, '', '/')
            )
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            r['currency_id'] = currency.browse(r.get('currency_id'))
            full_account.append(r)

        return full_account

    def _sum_partner(self, data, partner, field):
        """
        Hérite de la méthode _sum_partner pour exclure les factures marquées
        comme 'exclude_from_partner_ledger'
        """
        if field not in ['debit', 'credit', 'debit - credit']:
            return

        result = 0.0
        query_get_data = self.env['account.move.line'].with_context(
            data['form'].get('used_context', {})
        )._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else \
            ' AND "account_move_line".full_reconcile_id IS NULL '

        # Clause d'exclusion pour les factures marquées
        exclude_clause = ' AND (m.exclude_from_partner_ledger IS NULL OR m.exclude_from_partner_ledger = FALSE) '

        params = [
            partner.id,
            tuple(data['computed']['move_state']),
            tuple(data['computed']['account_ids'])
        ] + query_get_data[2]

        query = """SELECT sum(""" + field + """)
                FROM """ + query_get_data[0] + """, account_move AS m
                WHERE "account_move_line".partner_id = %s
                    AND m.id = "account_move_line".move_id
                    AND m.state IN %s
                    AND account_id IN %s
                    AND """ + query_get_data[1] + reconcile_clause + exclude_clause

        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        if contemp is not None:
            result = contemp[0] or 0.0

        return result
