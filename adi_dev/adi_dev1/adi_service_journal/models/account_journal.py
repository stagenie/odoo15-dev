# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_service_journal = fields.Boolean(
        string='Journal Service',
        default=False,
        help="Cocher pour indiquer que ce journal est dédié aux achats de service. "
             "Ce journal sera proposé uniquement pour les factures fournisseur de type service."
    )

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        """Surcharge pour filtrer les journaux service selon le contexte."""
        args = args or []
        context = self._context or {}

        # Si le contexte demande uniquement les journaux de service
        if context.get('service_journal_only'):
            args = args + [('is_service_journal', '=', True)]
        # Si le contexte demande d'exclure les journaux de service
        elif context.get('exclude_service_journal'):
            args = args + [('is_service_journal', '=', False)]

        return super(AccountJournal, self)._name_search(
            name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid
        )
