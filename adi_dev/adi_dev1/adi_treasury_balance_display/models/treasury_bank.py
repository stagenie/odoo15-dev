# -*- coding: utf-8 -*-
"""
Module: adi_treasury_balance_display
=====================================

Ce module étend treasury.bank pour afficher les soldes détaillés :
- Solde Actuel (corrigé)
- Solde Rapproché
- Solde Non Rapproché

CORRECTION APPORTÉE:
--------------------
Le module adi_treasury_bank original calcule current_balance uniquement
avec les opérations state='posted', ignorant celles avec state='reconciled'.

Bug original (adi_treasury_bank/models/treasury_bank.py ligne 233-236):
    operations = self.env['treasury.bank.operation'].search([
        ('bank_id', '=', bank.id),
        ('state', '=', 'posted')  # ← Ignore 'reconciled' !
    ])

Ce module surcharge _compute_current_balance() pour inclure les deux états:
    ('state', 'in', ['posted', 'reconciled'])

FORMULES:
---------
- Solde Actuel = Toutes opérations (posted + reconciled)
- Solde Rapproché = Opérations avec is_reconciled=True OU state='reconciled'
- Solde Non Rapproché = Opérations avec is_reconciled=False ET state='posted'
- Vérification: Solde Actuel = Solde Rapproché + Solde Non Rapproché
"""

from odoo import models, fields, api, _


class TreasuryBankBalanceDisplay(models.Model):
    _inherit = 'treasury.bank'

    # =========================================================================
    # NOUVEAUX CHAMPS
    # =========================================================================

    reconciled_balance = fields.Monetary(
        string='Solde Rapproché',
        compute='_compute_all_balances',
        store=True,
        currency_field='currency_id',
        help="Solde des opérations rapprochées avec le relevé bancaire"
    )

    unreconciled_balance = fields.Monetary(
        string='Solde Non Rapproché',
        compute='_compute_all_balances',
        store=True,
        currency_field='currency_id',
        help="Solde des opérations en attente de rapprochement"
    )

    # =========================================================================
    # SURCHARGE: Correction du calcul current_balance
    # =========================================================================

    @api.depends(
        'operation_ids',
        'operation_ids.state',
        'operation_ids.amount',
        'operation_ids.operation_type',
        'operation_ids.is_reconciled',
        'closing_ids.state',
        'closing_ids.balance_end_bank'
    )
    def _compute_current_balance(self):
        """
        SURCHARGE: Corrige le calcul du solde actuel.

        CORRECTION: Inclut les opérations 'posted' ET 'reconciled'.
        Le module original n'incluait que 'posted'.
        """
        for bank in self:
            # Chercher la dernière clôture validée
            last_closing = self.env['treasury.bank.closing'].search([
                ('bank_id', '=', bank.id),
                ('state', '=', 'validated')
            ], order='closing_date desc, id desc', limit=1)

            if last_closing:
                # Partir du solde de la dernière clôture
                balance = last_closing.balance_end_bank

                # CORRECTION: Inclure 'posted' ET 'reconciled'
                operations = self.env['treasury.bank.operation'].search([
                    ('bank_id', '=', bank.id),
                    ('state', 'in', ['posted', 'reconciled']),  # ← CORRIGÉ
                    ('date', '>', last_closing.closing_date),
                    '|',
                    ('closing_id', '=', False),
                    ('closing_id.state', '!=', 'validated')
                ])
            else:
                # Pas de clôture validée : partir de zéro
                balance = 0.0
                # CORRECTION: Inclure 'posted' ET 'reconciled'
                operations = self.env['treasury.bank.operation'].search([
                    ('bank_id', '=', bank.id),
                    ('state', 'in', ['posted', 'reconciled'])  # ← CORRIGÉ
                ])

            # Calculer le solde
            for op in operations:
                if op.operation_type == 'in':
                    balance += op.amount
                else:
                    balance -= op.amount

            bank.current_balance = balance

    # =========================================================================
    # CALCUL DES SOLDES RAPPROCHÉ ET NON RAPPROCHÉ
    # =========================================================================

    @api.depends(
        'operation_ids',
        'operation_ids.state',
        'operation_ids.amount',
        'operation_ids.operation_type',
        'operation_ids.is_reconciled',
        'closing_ids.state',
        'closing_ids.balance_end_bank'
    )
    def _compute_all_balances(self):
        """
        Calcule les soldes rapprochés et non rapprochés.

        - Solde Rapproché: opérations avec is_reconciled=True ou state='reconciled'
        - Solde Non Rapproché: opérations avec is_reconciled=False et state='posted'
        """
        for bank in self:
            # Chercher la dernière clôture validée
            last_closing = self.env['treasury.bank.closing'].search([
                ('bank_id', '=', bank.id),
                ('state', '=', 'validated')
            ], order='closing_date desc, id desc', limit=1)

            if last_closing:
                # Le solde de la dernière clôture est considéré comme rapproché
                base_reconciled_balance = last_closing.balance_end_bank

                # Récupérer les opérations postérieures à la clôture
                domain = [
                    ('bank_id', '=', bank.id),
                    ('state', 'in', ['posted', 'reconciled']),
                    ('date', '>', last_closing.closing_date),
                    '|',
                    ('closing_id', '=', False),
                    ('closing_id.state', '!=', 'validated')
                ]
            else:
                # Pas de clôture validée : partir de zéro
                base_reconciled_balance = 0.0
                domain = [
                    ('bank_id', '=', bank.id),
                    ('state', 'in', ['posted', 'reconciled'])
                ]

            operations = self.env['treasury.bank.operation'].search(domain)

            # Calculer les soldes séparément
            reconciled_amount = 0.0
            unreconciled_amount = 0.0

            for op in operations:
                # Calculer le montant signé
                if op.operation_type == 'in':
                    signed_amount = op.amount
                else:
                    signed_amount = -op.amount

                # Répartir selon le statut de rapprochement
                if op.is_reconciled or op.state == 'reconciled':
                    reconciled_amount += signed_amount
                else:
                    unreconciled_amount += signed_amount

            # Affecter les valeurs
            bank.reconciled_balance = base_reconciled_balance + reconciled_amount
            bank.unreconciled_balance = unreconciled_amount
