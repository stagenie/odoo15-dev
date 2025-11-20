from odoo import models, api, fields, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Champs calculés pour afficher le solde et la limite de crédit du client
    customer_balance = fields.Float(
        string='Solde client',
        compute='_compute_customer_balance',
        readonly=True,
        help='Solde actuel du client (factures ouvertes - paiements - avoirs)'
    )

    available_credit = fields.Float(
        string='Crédit disponible',
        compute='_compute_available_credit',
        readonly=True,
        help='Crédit disponible = Limite de crédit - Solde actuel'
    )

    partner_credit_limit = fields.Float(
        string='Limite de crédit',
        related='partner_id.credit_limit',
        readonly=True,
        help='Limite de crédit du partenaire'
    )

    @api.depends('partner_id')
    def _compute_customer_balance(self):
        """Calcule le solde client en utilisant la méthode existante."""
        for order in self:
            if order.partner_id:
                order.customer_balance = self._get_customer_balance(order.partner_id)
            else:
                order.customer_balance = 0.0

    @api.depends('partner_id', 'customer_balance')
    def _compute_available_credit(self):
        """Calcule le crédit disponible."""
        for order in self:
            if order.partner_id and order.partner_id.credit_limit_active:
                order.available_credit = order.partner_id.credit_limit - order.customer_balance
            else:
                order.available_credit = 0.0

    def _get_customer_balance(self, partner):
        """
        Calcul du solde total actuel d'un client :
        - Total des factures ouvertes (montant résiduel).
        - Moins les paiements non affectés (paiements sans factures liées).
        - Moins les avoirs non utilisés.
        """
        # 1. Calculer le total des factures ouvertes
        total_invoices = sum(partner.invoice_ids.filtered(
            lambda inv: inv.state in ['posted'] and not inv.payment_state == 'paid'
        ).mapped('amount_residual'))

        # 2. Calculer les paiements non affectés (paiements sans factures liées)
        payments = self.env['account.payment'].search([
            ('partner_id', '=', partner.id),
            ('state', '=', 'posted'),
        ])
        total_payments = sum(payment.amount for payment in payments if not payment.reconciled_invoice_ids)

        # 3. Calculer les avoirs non utilisés
        credits = partner.invoice_ids.filtered(
            lambda inv: inv.state in ['posted'] and inv.move_type == 'out_refund' and inv.payment_state != 'paid'
        )
        total_credits = sum(credits.mapped('amount_residual'))

        # Solde total = factures - paiements - avoirs
        return total_invoices - total_payments - total_credits

    def check_credit_limit(self):
        """
        Vérifie la limite de crédit du client avant de confirmer la commande.
        """
        for order in self:
            partner = order.partner_id

            # Vérifier si la limite de crédit est activée pour ce client
            if partner.credit_limit_active:
                # Appeler la méthode pour calculer le solde actuel
                total_due = self._get_customer_balance(partner)

                # Ajouter le montant de la commande en cours
                total_due += order.amount_total

                # Vérifier si le solde dépasse la limite
                if total_due > partner.credit_limit:
                    raise UserError(_(
                        "La commande ne peut pas être confirmée.\n"
                        "Le client '%s' a atteint sa limite de crédit.\n"
                        "Limite de crédit : %.2f\n"
                        "Solde actuel : %.2f\n"
                        "Montant de la commande : %.2f"
                    ) % (partner.name, partner.credit_limit, total_due - order.amount_total, order.amount_total))

    def action_confirm(self):
        """
        Surcharge de la méthode pour vérifier la limite de crédit avant validation.
        """
        # Appeler la vérification de la limite de crédit uniquement lors de la confirmation
        self.check_credit_limit()
        return super(SaleOrder, self).action_confirm()