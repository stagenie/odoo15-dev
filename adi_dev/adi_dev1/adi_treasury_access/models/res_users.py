# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    # =========================================================================
    # CHAMPS CALCULÉS POUR LES ACCÈS
    # =========================================================================

    treasury_cash_ids = fields.Many2many(
        'treasury.cash',
        string='Caisses autorisées',
        compute='_compute_treasury_access',
        search='_search_treasury_cash_ids'
    )

    treasury_safe_ids = fields.Many2many(
        'treasury.safe',
        string='Coffres autorisés',
        compute='_compute_treasury_access',
        search='_search_treasury_safe_ids'
    )

    treasury_bank_ids = fields.Many2many(
        'treasury.bank',
        string='Banques autorisées',
        compute='_compute_treasury_access',
        search='_search_treasury_bank_ids'
    )

    has_treasury_cash = fields.Boolean(
        string='A accès aux caisses',
        compute='_compute_treasury_access'
    )

    has_treasury_safe = fields.Boolean(
        string='A accès aux coffres',
        compute='_compute_treasury_access'
    )

    has_treasury_bank = fields.Boolean(
        string='A accès aux banques',
        compute='_compute_treasury_access'
    )

    # =========================================================================
    # CALCULS
    # =========================================================================

    @api.depends_context('uid')
    def _compute_treasury_access(self):
        """Calculer les entités de trésorerie accessibles par l'utilisateur"""
        Cash = self.env['treasury.cash']
        Safe = self.env['treasury.safe']
        Bank = self.env['treasury.bank']

        for user in self:
            # Vérifier si manager
            is_manager = user.has_group('adi_treasury.group_treasury_manager')

            if is_manager:
                # Manager voit tout
                user.treasury_cash_ids = Cash.search([])
                user.treasury_safe_ids = Safe.search([])
                user.treasury_bank_ids = Bank.search([])
            else:
                # Utilisateur normal - filtrer par accès
                user.treasury_cash_ids = Cash.search([
                    '|', '|',
                    ('user_ids', 'in', [user.id]),
                    ('responsible_id', '=', user.id),
                    ('create_uid', '=', user.id)
                ])

                user.treasury_safe_ids = Safe.search([
                    '|',
                    ('responsible_ids', 'in', [user.id]),
                    ('create_uid', '=', user.id)
                ])

                user.treasury_bank_ids = Bank.search([
                    '|', '|',
                    ('user_ids', 'in', [user.id]),
                    ('responsible_id', '=', user.id),
                    ('create_uid', '=', user.id)
                ])

            # Booléens pour les menus
            user.has_treasury_cash = bool(user.treasury_cash_ids)
            user.has_treasury_safe = bool(user.treasury_safe_ids)
            user.has_treasury_bank = bool(user.treasury_bank_ids)

    def _search_treasury_cash_ids(self, operator, value):
        """Recherche pour le champ treasury_cash_ids"""
        return [('id', 'in', self.env['treasury.cash'].search([]).mapped('user_ids').ids)]

    def _search_treasury_safe_ids(self, operator, value):
        """Recherche pour le champ treasury_safe_ids"""
        return [('id', 'in', self.env['treasury.safe'].search([]).mapped('responsible_ids').ids)]

    def _search_treasury_bank_ids(self, operator, value):
        """Recherche pour le champ treasury_bank_ids"""
        return [('id', 'in', self.env['treasury.bank'].search([]).mapped('user_ids').ids)]
