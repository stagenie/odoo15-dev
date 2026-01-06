# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.osv import expression


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_hidden = fields.Boolean(
        string='Masqué',
        default=False,
        help="Si coché, ce journal sera masqué pour tous les utilisateurs "
             "qui n'ont pas le droit 'Voir journaux masqués'."
    )

    def _get_hidden_domain(self):
        """Retourne le domain pour filtrer les journaux masqués."""
        if self.env.user.has_group('adi_journal_visibility.group_see_hidden_journals'):
            return []
        return [('is_hidden', '=', False)]

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        """Surcharge _search pour filtrer les journaux masqués."""
        args = expression.AND([args or [], self._get_hidden_domain()])
        return super(AccountJournal, self)._search(
            args, offset=offset, limit=limit, order=order,
            count=count, access_rights_uid=access_rights_uid
        )

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Surcharge pour filtrer les journaux masqués."""
        args = expression.AND([args or [], self._get_hidden_domain()])
        return super(AccountJournal, self).search(
            args, offset=offset, limit=limit, order=order, count=count
        )

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Surcharge pour filtrer les journaux masqués dans les champs de sélection."""
        args = expression.AND([args or [], self._get_hidden_domain()])
        return super(AccountJournal, self).name_search(
            name=name, args=args, operator=operator, limit=limit
        )

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """Surcharge pour filtrer les journaux masqués dans les vues groupées."""
        domain = expression.AND([domain or [], self._get_hidden_domain()])
        return super(AccountJournal, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy
        )
