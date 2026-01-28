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

        Le mode de calcul dépend de la configuration globale:
        - Mode 'receivable': Solde client uniquement (comptes receivable)
        - Mode 'net': Solde net (comptes receivable + payable)

        SUM(balance) sur les account_move_line :
        - Pour les mouvements postés (state = 'posted')
        - En excluant les factures marquées exclude_from_partner_ledger = True

        Retourne un solde positif si le client nous doit de l'argent.
        """
        self.ensure_one()

        if not self.id:
            return 0.0

        # Récupérer le mode de calcul depuis la configuration
        balance_mode = self.env['ir.config_parameter'].sudo().get_param(
            'adi_partner_credit_limit.partner_balance_mode', 'receivable'
        )

        # Définir le filtre sur les types de compte selon le mode
        if balance_mode == 'net':
            # Mode net: inclure receivable ET payable
            account_type_clause = "aa.internal_type IN ('receivable', 'payable')"
        else:
            # Mode receivable (par défaut): uniquement les créances client
            account_type_clause = "aa.internal_type = 'receivable'"

        # Calculer le solde via SQL
        self.env.cr.execute("""
            SELECT COALESCE(SUM(aml.balance), 0)
            FROM account_move_line aml
            JOIN account_move m ON m.id = aml.move_id
            JOIN account_account aa ON aa.id = aml.account_id
            WHERE aml.partner_id = %s
                AND m.state = 'posted'
                AND """ + account_type_clause + """
                AND (m.exclude_from_partner_ledger IS NULL OR m.exclude_from_partner_ledger = FALSE)
        """, (self.id,))

        result = self.env.cr.fetchone()
        return result[0] if result else 0.0
