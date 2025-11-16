# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    def _adapt_account_groups_parent(self):
        account_group_obj = self.env['account.group']

        # Comptes de bilan
        classes_15 = account_group_obj.search([('code_prefix_start', 'in', ['1', '2', '3', '4', '5'])])
        comptes_bilan = account_group_obj.search([('code_prefix_start', '=', "!1-5")])
        classes_15.write({'parent_id': comptes_bilan})

        # Comptes de gestion
        classes_67 = account_group_obj.search([('code_prefix_start', 'in', ['6', '7'])])
        comptes_gestion = account_group_obj.search([('code_prefix_start', '=', "!6-7")])
        classes_67.write({'parent_id': comptes_gestion})

        # Comptes spéciaux
        classes_089 = account_group_obj.search([('code_prefix_start', 'in', ['0', '8', '9'])])
        comptes_speciaux = account_group_obj.search([('code_prefix_start', '=', "!0-8-9")])
        classes_089.write({'parent_id': comptes_speciaux})

        # Système Comptable Financier Algérien
        (comptes_bilan + comptes_gestion + comptes_speciaux).write({
            'parent_id': account_group_obj.search([('code_prefix_start', '=', "!")])
        })

    def _load(self, sale_tax_rate, purchase_tax_rate, company):
        res = super(AccountChartTemplate, self)._load(sale_tax_rate, purchase_tax_rate, company)

        if self.id == self.env.ref('dns_l10n_dz_scf.l10n_dz_scf_pcg_chart_template').id:
            account_ids = self.env['account.account'].search([])
            self.env['account.group']._adapt_accounts_for_account_groups(account_ids)
            self._adapt_account_groups_parent()

        return res
