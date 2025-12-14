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

    def _get_customer_balance(self, partner):
        """
        Calcul du solde total actuel d'un client.

        Utilise la même logique que le rapport Partner Ledger (accounting_pdf_reports) :
        - SUM(debit - credit) sur les account_move_line
        - Sur les comptes de type "receivable"
        - Pour les mouvements postés (state = 'posted')
        - En excluant les factures marquées avec exclude_from_partner_ledger = True

        Cette approche garantit la cohérence avec le rapport Partner Ledger.
        """
        # Récupérer les comptes de type "receivable" (comptes clients)
        self.env.cr.execute("""
            SELECT id FROM account_account
            WHERE internal_type = 'receivable'
            AND NOT deprecated
        """)
        account_ids = [row[0] for row in self.env.cr.fetchall()]

        if not account_ids:
            return 0.0

        # Calculer le solde : SUM(debit - credit) sur les lignes comptables
        # Même logique que _sum_partner dans accounting_pdf_reports
        self.env.cr.execute("""
            SELECT COALESCE(SUM(aml.debit - aml.credit), 0)
            FROM account_move_line aml
            JOIN account_move m ON m.id = aml.move_id
            WHERE aml.partner_id = %s
                AND m.state = 'posted'
                AND aml.account_id IN %s
                AND (m.exclude_from_partner_ledger IS NULL OR m.exclude_from_partner_ledger = FALSE)
        """, (partner.id, tuple(account_ids)))

        result = self.env.cr.fetchone()
        return result[0] if result else 0.0

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