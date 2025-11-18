# -*- coding: utf-8 -*-

from odoo import models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _query_get(self, domain=None):
        """
        Hérite de _query_get pour ajouter automatiquement l'exclusion des factures marquées
        dans toutes les requêtes comptables
        """
        tables, where_clause, where_params = super()._query_get(domain=domain)

        # Ajouter la clause d'exclusion seulement si nous sommes dans un contexte de rapport
        # ou de vue comptable (Partner Ledger, General Ledger, etc.)
        context = self.env.context
        if context.get('model') in ['report.accounting_pdf_reports.report_partnerledger',
                                     'report.accounting_pdf_reports.report_general_ledger',
                                     'account.report'] or \
           context.get('report_type') in ['partner_ledger', 'general_ledger'] or \
           context.get('exclude_flagged_moves', False):

            # Vérifier si la table account_move est déjà jointe
            if 'account_move' not in tables:
                tables += ' JOIN account_move ON account_move.id = account_move_line.move_id'

            # Ajouter la clause d'exclusion
            exclude_clause = '(account_move.exclude_from_partner_ledger IS NULL OR account_move.exclude_from_partner_ledger = FALSE)'
            if where_clause:
                where_clause = f"({where_clause}) AND {exclude_clause}"
            else:
                where_clause = exclude_clause

        return tables, where_clause, where_params

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """
        Surcharge search_read pour exclure les factures marquées dans les vues liste
        """
        context = self.env.context

        # Vérifier si nous sommes dans une vue comptable
        if context.get('exclude_flagged_moves', False) or \
           self._context.get('model') == 'account.move.line' and \
           any(view in str(context.get('params', {}).get('action', ''))
               for view in ['action_account_moves_ledger', 'action_move_line_select']):

            # Ajouter le domaine d'exclusion
            if domain is None:
                domain = []
            domain = domain + [('move_id.exclude_from_partner_ledger', '!=', True)]

        return super().search_read(domain=domain, fields=fields, offset=offset,
                                  limit=limit, order=order)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """
        Surcharge read_group pour exclure les factures marquées dans les regroupements
        """
        context = self.env.context

        # Vérifier si nous sommes dans une vue comptable avec regroupement
        if context.get('exclude_flagged_moves', False) or \
           context.get('report_type') in ['partner_ledger', 'general_ledger']:

            # Ajouter le domaine d'exclusion
            if domain is None:
                domain = []
            domain = domain + [('move_id.exclude_from_partner_ledger', '!=', True)]

        return super().read_group(domain, fields, groupby, offset=offset,
                                limit=limit, orderby=orderby, lazy=lazy)