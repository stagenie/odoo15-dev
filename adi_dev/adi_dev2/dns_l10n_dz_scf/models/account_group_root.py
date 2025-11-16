# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError

class AccountGroupRoot(models.Model):
    _name = 'account.group.root'
    _description = 'Account group codes first 2 digits'
    _auto = False

    name = fields.Char()
    parent_id = fields.Many2one('account.group.root')
    company_id = fields.Many2one('res.company')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
            SELECT DISTINCT ASCII(code_prefix_start) * 1000 + ASCII(SUBSTRING(code_prefix_start,2,1)) AS id,
                   LEFT(code_prefix_start,2) AS name,
                   ASCII(code_prefix_start) AS parent_id,
                   company_id
            FROM account_group WHERE code_prefix_start IS NOT NULL
            UNION ALL
            SELECT DISTINCT ASCII(code_prefix_start) AS id,
                   LEFT(code_prefix_start,1) AS name,
                   NULL::int AS parent_id,
                   company_id
            FROM account_group WHERE code_prefix_start IS NOT NULL
            )''' % (self._table,)
        )