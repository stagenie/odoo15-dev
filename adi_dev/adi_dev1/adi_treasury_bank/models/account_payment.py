# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Relation avec les opérations bancaires
    treasury_bank_operation_id = fields.Many2one(
        'treasury.bank.operation',
        string='Opération bancaire',
        readonly=True,
        help="Opération bancaire créée automatiquement pour ce paiement"
    )

    # Compte bancaire
    bank_id = fields.Many2one(
        'treasury.bank',
        string='Compte bancaire',
        compute='_compute_bank_id',
        store=True,
        readonly=True
    )

    @api.depends('journal_id')
    def _compute_bank_id(self):
        """Trouve le compte bancaire associé au journal"""
        for payment in self:
            if payment.journal_id and payment.journal_id.type == 'bank':
                bank = self.env['treasury.bank'].search([
                    ('journal_id', '=', payment.journal_id.id),
                    ('company_id', '=', payment.company_id.id)
                ], limit=1)
                payment.bank_id = bank
            else:
                payment.bank_id = False

    def action_post(self):
        """Surcharge de la validation pour créer une opération bancaire automatique"""
        # Appeler la méthode parente
        res = super(AccountPayment, self).action_post()

        # Pour chaque paiement validé
        for payment in self:
            # Vérifier si c'est un paiement bancaire
            if payment.journal_id.type == 'bank' and not payment.treasury_bank_operation_id:
                # Chercher le compte bancaire associé
                bank = self.env['treasury.bank'].search([
                    ('journal_id', '=', payment.journal_id.id),
                    ('company_id', '=', payment.company_id.id)
                ], limit=1)

                if bank:
                    # Vérifier que la banque est active
                    if bank.state != 'active':
                        raise UserError(_(
                            "Le compte bancaire '%s' n'est pas actif. "
                            "Impossible de créer l'opération bancaire."
                        ) % bank.name)

                    # Déterminer le type d'opération
                    if payment.payment_type == 'inbound':
                        operation_type = 'in'
                    else:
                        operation_type = 'out'

                    # Déterminer la catégorie selon le type de partenaire
                    category = self._get_bank_category(payment, operation_type)

                    # Déterminer la méthode de paiement
                    payment_method = self._get_bank_payment_method(payment)

                    # Créer l'opération bancaire automatiquement
                    operation = self.env['treasury.bank.operation'].create({
                        'name': self.env['ir.sequence'].next_by_code('treasury.bank.operation'),
                        'bank_id': bank.id,
                        'operation_type': operation_type,
                        'category_id': category.id if category else False,
                        'amount': payment.amount,
                        'date': fields.Datetime.now(),
                        'value_date': payment.date,
                        'description': payment.ref or payment.communication or '',
                        'partner_id': payment.partner_id.id if payment.partner_id else False,
                        'payment_id': payment.id,
                        'payment_method': payment_method,
                        'bank_reference': payment.name,
                        'is_manual': False,
                        'state': 'posted',  # Comptabiliser immédiatement
                    })

                    # Lien bidirectionnel
                    payment.treasury_bank_operation_id = operation.id

                    # Message de confirmation
                    payment.message_post(
                        body=_("Opération bancaire créée automatiquement : %s") % operation.name
                    )
                    operation.message_post(
                        body=_("Créée automatiquement depuis le paiement : %s") % payment.name
                    )

        return res

    def _get_bank_category(self, payment, operation_type):
        """Détermine la catégorie d'opération bancaire selon le paiement"""
        category = False

        # Déterminer selon le type de paiement et de partenaire
        if payment.payment_type == 'inbound':
            if payment.partner_type == 'customer':
                # Encaissement client
                category = self.env['treasury.operation.category'].search([
                    ('code', '=', 'BANK_CUSTOMER_IN')
                ], limit=1)
                if not category:
                    category = self.env['treasury.operation.category'].search([
                        ('is_customer_payment', '=', True),
                        ('operation_type', 'in', ['in', 'both'])
                    ], limit=1)
            elif payment.partner_type == 'supplier':
                # Remboursement fournisseur
                category = self.env['treasury.operation.category'].search([
                    ('code', '=', 'BANK_REFUND_SUPPLIER')
                ], limit=1)
        else:  # outbound
            if payment.partner_type == 'customer':
                # Remboursement client
                category = self.env['treasury.operation.category'].search([
                    ('code', '=', 'BANK_REFUND_CUSTOMER')
                ], limit=1)
            elif payment.partner_type == 'supplier':
                # Paiement fournisseur
                category = self.env['treasury.operation.category'].search([
                    ('code', '=', 'BANK_SUPPLIER_OUT')
                ], limit=1)
                if not category:
                    category = self.env['treasury.operation.category'].search([
                        ('is_vendor_payment', '=', True),
                        ('operation_type', 'in', ['out', 'both'])
                    ], limit=1)

        # Fallback : catégorie générique
        if not category:
            if operation_type == 'in':
                category = self.env['treasury.operation.category'].search([
                    ('code', '=', 'BANK_TRANSFER_IN')
                ], limit=1)
            else:
                category = self.env['treasury.operation.category'].search([
                    ('code', '=', 'BANK_TRANSFER_OUT')
                ], limit=1)

        return category

    def _get_bank_payment_method(self, payment):
        """Détermine la méthode de paiement bancaire"""
        # Essayer de déterminer selon le moyen de paiement
        if payment.payment_method_id:
            method_name = payment.payment_method_id.name.lower()
            if 'virement' in method_name or 'transfer' in method_name:
                return 'transfer'
            elif 'chèque' in method_name or 'check' in method_name or 'cheque' in method_name:
                return 'check'
            elif 'carte' in method_name or 'card' in method_name:
                return 'card'
            elif 'prélèvement' in method_name or 'debit' in method_name:
                return 'direct_debit'

        # Par défaut : virement
        return 'transfer'

    def action_cancel(self):
        """Surcharge de l'annulation pour gérer l'opération bancaire"""
        for payment in self:
            # Si une opération bancaire existe
            if payment.treasury_bank_operation_id:
                operation = payment.treasury_bank_operation_id

                # Vérifier si l'opération est dans une clôture validée
                if operation.closing_id and operation.closing_id.state == 'validated':
                    raise UserError(_(
                        "Impossible d'annuler ce paiement : "
                        "l'opération bancaire associée est incluse dans le rapprochement validé '%s'.\n"
                        "Veuillez d'abord annuler le rapprochement bancaire."
                    ) % operation.closing_id.name)

                # Vérifier si l'opération est rapprochée
                if operation.is_reconciled:
                    raise UserError(_(
                        "Impossible d'annuler ce paiement : "
                        "l'opération bancaire associée a été rapprochée avec un relevé.\n"
                        "Veuillez d'abord annuler le rapprochement de l'opération."
                    ))

                # Annuler l'opération bancaire
                operation.action_cancel()

        # Appeler la méthode parente
        return super(AccountPayment, self).action_cancel()

    def action_draft(self):
        """Surcharge du retour en brouillon pour gérer l'opération bancaire"""
        for payment in self:
            # Si une opération bancaire existe
            if payment.treasury_bank_operation_id:
                operation = payment.treasury_bank_operation_id

                # Vérifier si l'opération est dans une clôture validée
                if operation.closing_id and operation.closing_id.state in ['validated', 'confirmed']:
                    raise UserError(_(
                        "Impossible de remettre en brouillon : "
                        "l'opération bancaire associée est incluse dans le rapprochement '%s' (état: %s).\n"
                        "Veuillez d'abord annuler le rapprochement bancaire."
                    ) % (operation.closing_id.name, operation.closing_id.state))

                # Supprimer l'opération bancaire
                operation.unlink()
                payment.treasury_bank_operation_id = False

        # Appeler la méthode parente
        return super(AccountPayment, self).action_draft()

    def action_view_bank_operation(self):
        """Ouvre l'opération bancaire associée"""
        self.ensure_one()
        if not self.treasury_bank_operation_id:
            raise UserError(_("Aucune opération bancaire associée à ce paiement."))

        return {
            'name': _('Opération bancaire'),
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.bank.operation',
            'view_mode': 'form',
            'res_id': self.treasury_bank_operation_id.id,
            'target': 'current',
        }
