from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Solde actuel du client (calculé)
    current_balance = fields.Monetary(
        string="Solde actuel",
        compute='_compute_current_balance',
        currency_field='currency_id',
        help="Solde net du partenaire (créances - dettes). "
             "Positif = le client nous doit de l'argent. "
             "Négatif = nous devons de l'argent au client/fournisseur."
    )

    credit_limit_active = fields.Boolean(
        string="Activer la limite de crédit",
        default=False
    )
    credit_limit = fields.Float(
        string="Limite de crédit",
        help="Montant maximum autorisé pour ce client."
    )

    @api.depends('credit', 'debit')
    def _compute_current_balance(self):
        """
        Calcule le solde actuel du partenaire.
        Utilise la même logique que le rapport Partner Ledger.
        """
        for partner in self:
            partner.current_balance = partner._get_current_balance()

    def _get_current_balance(self):
        """
        Calcul du solde total actuel d'un partenaire.

        SUM(debit - credit) sur les account_move_line :
        - Sur les comptes de type "receivable" ET "payable"
        - Pour les mouvements postés (state = 'posted')
        - En excluant les factures marquées exclude_from_partner_ledger = True

        Retourne un solde positif si le client nous doit de l'argent.
        """
        self.ensure_one()

        if not self.id:
            return 0.0

        # Récupérer les comptes de type "receivable" et "payable"
        self.env.cr.execute("""
            SELECT id FROM account_account
            WHERE internal_type IN ('receivable', 'payable')
            AND NOT deprecated
        """)
        account_ids = [row[0] for row in self.env.cr.fetchall()]

        if not account_ids:
            return 0.0

        # Calculer le solde : SUM(debit - credit)
        self.env.cr.execute("""
            SELECT COALESCE(SUM(aml.debit - aml.credit), 0)
            FROM account_move_line aml
            JOIN account_move m ON m.id = aml.move_id
            WHERE aml.partner_id = %s
                AND m.state = 'posted'
                AND aml.account_id IN %s
                AND (m.exclude_from_partner_ledger IS NULL OR m.exclude_from_partner_ledger = FALSE)
        """, (self.id, tuple(account_ids)))

        result = self.env.cr.fetchone()
        return result[0] if result else 0.0
