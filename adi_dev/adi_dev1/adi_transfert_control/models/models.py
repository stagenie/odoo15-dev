from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, _logger


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    source_journal_balance = fields.Monetary(
        string='Solde Journal Source (qui donne)',
        compute='_compute_journal_balances',
        currency_field='currency_id',
        store=False,
        help='Solde du journal qui donne l\'argent'
    )

    destination_journal_balance = fields.Monetary(
        string='Solde Journal Destination (qui reçoit)',
        compute='_compute_journal_balances',
        currency_field='currency_id',
        store=False,
        help='Solde du journal qui reçoit l\'argent'
    )

    is_amount_exceeds_balance = fields.Boolean(
        string='Montant Supérieur au Solde',
        compute='_compute_amount_exceeds_balance',
        store=False,
        help='Indique si le montant du transfert dépasse le solde du journal qui donne'
    )

    source_journal_name = fields.Char(
        string='Nom Journal Source',
        compute='_compute_journal_names',
        store=False,
        help='Nom du journal qui donne l\'argent'
    )

    destination_journal_name = fields.Char(
        string='Nom Journal Destination',
        compute='_compute_journal_names',
        store=False,
        help='Nom du journal qui reçoit l\'argent'
    )

    @api.depends('destination_journal_id', 'journal_id', 'payment_type', 'is_internal_transfer', 'state')
    def _compute_journal_names(self):
        """Détermine les noms des journaux source et destination"""
        for payment in self:
            payment.source_journal_name = ''
            payment.destination_journal_name = ''

            if payment.is_internal_transfer:
                if payment.payment_type == 'outbound':
                    # Envoyer : journal_id DONNE vers destination_journal_id
                    payment.source_journal_name = payment.journal_id.name if payment.journal_id else ''
                    payment.destination_journal_name = payment.destination_journal_id.name if payment.destination_journal_id else ''
                else:
                    # Recevoir : destination_journal_id DONNE vers journal_id
                    payment.source_journal_name = payment.destination_journal_id.name if payment.destination_journal_id else ''
                    payment.destination_journal_name = payment.journal_id.name if payment.journal_id else ''

    @api.depends('destination_journal_id', 'journal_id', 'payment_type', 'is_internal_transfer', 'state', 'move_id')
    def _compute_journal_balances(self):
        """Calcule les soldes des journaux - toujours identifier qui DONNE et qui REÇOIT"""
        for payment in self:
            payment.source_journal_balance = 0.0
            payment.destination_journal_balance = 0.0

            if payment.is_internal_transfer:
                if payment.payment_type == 'outbound':
                    # Envoyer : journal_id DONNE vers destination_journal_id
                    if payment.journal_id:
                        payment.source_journal_balance = self._get_journal_balance(payment.journal_id)
                    if payment.destination_journal_id:
                        payment.destination_journal_balance = self._get_journal_balance(payment.destination_journal_id)
                else:
                    # Recevoir : destination_journal_id DONNE vers journal_id
                    if payment.destination_journal_id:
                        payment.source_journal_balance = self._get_journal_balance(payment.destination_journal_id)
                    if payment.journal_id:
                        payment.destination_journal_balance = self._get_journal_balance(payment.journal_id)

    @api.depends('amount', 'source_journal_balance', 'is_internal_transfer', 'state')
    def _compute_amount_exceeds_balance(self):
        """Vérifie si le montant dépasse le solde du journal qui DONNE l'argent (uniquement en brouillon)"""
        for payment in self:
            if payment.state == 'draft' and payment.is_internal_transfer:
                payment.is_amount_exceeds_balance = payment.amount > payment.source_journal_balance
            else:
                payment.is_amount_exceeds_balance = False

    def _get_journal_balance(self, journal):
        """Récupère le solde RÉEL d'un journal en temps réel"""
        if not journal or not journal.default_account_id:
            return 0.0

        account = journal.default_account_id

        # Utiliser une requête SQL directe pour le solde le plus précis
        # N'inclure QUE les mouvements validés (posted), pas les brouillons
        self.env.cr.execute("""
            SELECT COALESCE(SUM(debit), 0) - COALESCE(SUM(credit), 0) as balance
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            WHERE aml.account_id = %s
                AND am.state = 'posted'
                AND (aml.payment_id IS NULL OR aml.payment_id != %s)
                AND aml.move_id NOT IN (
                    SELECT move_id FROM account_payment WHERE id = %s AND move_id IS NOT NULL
                )
        """, (account.id, self.id or 0, self.id or 0))

        result = self.env.cr.fetchone()
        balance = result[0] if result else 0.0

        return balance

    def action_post(self):
        """Override pour vérifier le solde AVANT validation et rafraîchir APRÈS"""
        # ÉTAPE 1 : Vérifier le solde AVANT de faire quoi que ce soit
        for payment in self:
            if payment.is_internal_transfer and payment.state == 'draft':
                # Déterminer le journal source (qui donne)
                if payment.payment_type == 'outbound':
                    source_journal = payment.journal_id
                else:
                    source_journal = payment.destination_journal_id

                if source_journal and source_journal.default_account_id:
                    # Calculer le solde MAINTENANT, avant toute opération
                    account = source_journal.default_account_id

                    # Requête SQL ultra-simple : ne compter QUE les moves validés
                    self.env.cr.execute("""
                        SELECT COALESCE(SUM(debit), 0) - COALESCE(SUM(credit), 0) as balance
                        FROM account_move_line aml
                        JOIN account_move am ON aml.move_id = am.id
                        WHERE aml.account_id = %s
                            AND am.state = 'posted'
                    """, (account.id,))

                    result = self.env.cr.fetchone()
                    balance = result[0] if result else 0.0

                    # DEBUG: Log pour comprendre ce qui se passe
                    _logger.info("=== VALIDATION TRANSFERT ===")
                    _logger.info(f"Journal source: {source_journal.name}")
                    _logger.info(f"Solde calculé: {balance}")
                    _logger.info(f"Montant demandé: {payment.amount}")
                    _logger.info(f"Test: {balance} < {payment.amount} = {balance < payment.amount}")

                    # Vérifier si le solde est suffisant
                    if balance < payment.amount:
                        action = "envoyer depuis" if payment.payment_type == 'outbound' else "recevoir depuis"

                        raise ValidationError(_(
                            '❌ Solde insuffisant!\n\n'
                            '📁 Journal qui donne: %s\n'
                            '🔄 Action: %s ce journal\n'
                            '💰 Solde disponible: %.2f %s\n'
                            '💸 Montant demandé: %.2f %s\n'
                            '⚠️ Manquant: %.2f %s\n\n'
                            '⛔ Ce transfert ne peut pas être effectué.\n'
                            'Veuillez réduire le montant ou approvisionner "%s".'
                        ) % (
                                                  source_journal.name,
                                                  action,
                                                  balance,
                                                  payment.currency_id.symbol,
                                                  payment.amount,
                                                  payment.currency_id.symbol,
                                                  payment.amount - balance,
                                                  payment.currency_id.symbol,
                                                  source_journal.name
                                              ))

        # ÉTAPE 2 : Valider le paiement
        res = super(AccountPayment, self).action_post()

        # ÉTAPE 3 : Forcer le rafraîchissement du cache (compatible Odoo v15)
        self.invalidate_cache()

        # ÉTAPE 4 : Retourner une action pour recharger la vue
        if len(self) == 1:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Transfert validé'),
                    'message': _('Le transfert a été validé avec succès. Les soldes ont été mis à jour.'),
                    'type': 'success',
                    'next': {
                        'type': 'ir.actions.act_window',
                        'res_model': 'account.payment',
                        'res_id': self.id,
                        'views': [[False, 'form']],
                        'view_mode': 'form',
                        'target': 'current',
                    }
                }
            }

        return res


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _check_balanced(self):
        """Override pour ajouter la vérification des soldes sur les virements manuels"""
        res = super(AccountMove, self)._check_balanced()

        for move in self:
            if move.move_type in ['entry'] and move.journal_id.type in ['cash', 'bank']:
                self._validate_manual_transfer_balance(move)

        return res

    def _validate_manual_transfer_balance(self, move):
        """Valide les virements manuels"""
        for line in move.line_ids.filtered(lambda l: l.credit > 0):
            # Dans Odoo v15, utiliser user_type_id.type au lieu de account_type
            if line.account_id.user_type_id and line.account_id.user_type_id.type in ['liquidity']:
                domain = [
                    ('account_id', '=', line.account_id.id),
                    ('parent_state', '=', 'posted'),
                    ('move_id', '!=', move.id),
                ]

                existing_lines = self.env['account.move.line'].search(domain)
                balance = sum(existing_lines.mapped('debit')) - sum(existing_lines.mapped('credit'))

                if balance < line.credit:
                    raise ValidationError(_(
                        '❌ Solde insuffisant sur le compte "%s"!\n\n'
                        '💰 Solde actuel: %.2f\n'
                        '💸 Montant du crédit: %.2f\n'
                        '⚠️ Manquant: %.2f\n\n'
                        'Cette opération ne peut pas être validée.'
                    ) % (
                                              line.account_id.display_name,
                                              balance,
                                              line.credit,
                                              line.credit - balance
                                          ))
