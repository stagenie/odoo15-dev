# -*- coding: utf-8 -*-

from odoo import api, fields, models

# Types d'opération qui augmentent le solde du coffre
# (même liste que treasury.safe._compute_current_balance)
IN_TYPES = ('initial', 'bank_in', 'other_in', 'adjustment')


class TreasurySafeOperationBalanceDisplayFix(models.Model):
    _inherit = 'treasury.safe.operation'

    has_balance_snapshot = fields.Boolean(
        string='Soldes enregistrés',
        readonly=True,
        copy=False,
        help="Soldes avant/après enregistrés au moment où l'opération a été effectuée",
    )
    balance_before_snapshot = fields.Monetary(
        string='Solde avant (enregistré)',
        currency_field='currency_id',
        readonly=True,
        copy=False,
    )
    balance_after_snapshot = fields.Monetary(
        string='Solde après (enregistré)',
        currency_field='currency_id',
        readonly=True,
        copy=False,
    )
    show_balances = fields.Boolean(compute='_compute_balances')

    def _get_balance_sign(self):
        self.ensure_one()
        return 1 if self.operation_type in IN_TYPES else -1

    @api.depends('safe_id', 'safe_id.current_balance', 'amount', 'operation_type', 'state',
                 'has_balance_snapshot', 'balance_before_snapshot', 'balance_after_snapshot')
    def _compute_balances(self):
        """Soldes avant/après (version corrigée).

        - Effectué avec soldes enregistrés : valeurs figées à la validation.
        - Brouillon / Confirmé : solde actuel du coffre, et solde prévu après.
        - Sinon (effectué avant ce module, annulé) : pas de valeur fiable.
        """
        for operation in self:
            if operation.state == 'done' and operation.has_balance_snapshot:
                operation.balance_before = operation.balance_before_snapshot
                operation.balance_after = operation.balance_after_snapshot
                operation.show_balances = True
            elif operation.safe_id and operation.state in ('draft', 'confirmed'):
                before = operation.safe_id.current_balance
                operation.balance_before = before
                operation.balance_after = before + operation._get_balance_sign() * operation.amount
                operation.show_balances = True
            else:
                operation.balance_before = 0
                operation.balance_after = 0
                operation.show_balances = False

    def action_done(self):
        """Enregistrer les soldes réels au moment où l'opération est effectuée."""
        for operation in self:
            safe = operation.safe_id
            safe._compute_current_balance()
            balance_before = safe.current_balance
            super(TreasurySafeOperationBalanceDisplayFix, operation).action_done()
            operation.write({
                'has_balance_snapshot': True,
                'balance_before_snapshot': balance_before,
                'balance_after_snapshot': balance_before + operation._get_balance_sign() * operation.amount,
            })
        return True
