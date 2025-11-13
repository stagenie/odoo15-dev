# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends_context('company')
    def _credit_debit_get(self):
        """
        Surcharge de la méthode pour exclure les factures marquées avec
        exclude_from_partner_balance = True du calcul des soldes
        """
        if not self.ids:
            self.debit = False
            self.credit = False
            return

        tables, where_clause, where_params = self.env['account.move.line'].with_context(
            state='posted', company_id=self.env.company.id
        )._query_get()
        where_params = [tuple(self.ids)] + where_params

        if where_clause:
            where_clause = 'AND ' + where_clause

        # Ajout de la condition pour exclure les lignes marquées
        exclude_clause = "AND (account_move_line.exclude_from_partner_balance IS NULL OR account_move_line.exclude_from_partner_balance = FALSE)"

        self._cr.execute("""SELECT account_move_line.partner_id, act.type, SUM(account_move_line.amount_residual)
                      FROM """ + tables + """
                      LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
                      LEFT JOIN account_account_type act ON (a.user_type_id=act.id)
                      WHERE act.type IN ('receivable','payable')
                      AND account_move_line.partner_id IN %s
                      AND account_move_line.reconciled IS NOT TRUE
                      """ + where_clause + """
                      """ + exclude_clause + """
                      GROUP BY account_move_line.partner_id, act.type
                      """, where_params)

        treated = self.browse()
        for pid, type, val in self._cr.fetchall():
            partner = self.browse(pid)
            if type == 'receivable':
                partner.credit = val
                if partner not in treated:
                    partner.debit = False
                    treated |= partner
            elif type == 'payable':
                partner.debit = -val
                if partner not in treated:
                    partner.credit = False
                    treated |= partner

        remaining = (self - treated)
        remaining.debit = False
        remaining.credit = False

    def _asset_difference_search(self, account_type, operator, operand):
        """
        Surcharge de la méthode pour exclure les factures marquées avec
        exclude_from_partner_balance = True de la recherche sur les soldes
        """
        if operator not in ('<', '=', '>', '>=', '<='):
            return []
        if not isinstance(operand, (float, int)):
            return []

        sign = 1
        if account_type == 'payable':
            sign = -1

        # Ajout de la condition pour exclure les lignes marquées
        res = self._cr.execute('''
            SELECT partner.id
            FROM res_partner partner
            LEFT JOIN account_move_line aml ON aml.partner_id = partner.id
            JOIN account_move move ON move.id = aml.move_id
            RIGHT JOIN account_account acc ON aml.account_id = acc.id
            WHERE acc.internal_type = %s
              AND NOT acc.deprecated AND acc.company_id = %s
              AND move.state = 'posted'
              AND (aml.exclude_from_partner_balance IS NULL OR aml.exclude_from_partner_balance = FALSE)
            GROUP BY partner.id
            HAVING %s * COALESCE(SUM(aml.amount_residual), 0) ''' + operator + ''' %s''',
            (account_type, self.env.company.id, sign, operand))

        res = self._cr.fetchall()
        if not res:
            return [('id', '=', '0')]
        return [('id', 'in', [r[0] for r in res])]
