from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Champs pour afficher le solde et la limite de crédit
    customer_balance = fields.Float(
        string='Solde client',
        compute='_compute_customer_credit_info',
        readonly=True,
        help='Solde net du partenaire'
    )
    partner_credit_limit = fields.Float(
        string='Limite de crédit',
        compute='_compute_customer_credit_info',
        readonly=True,
        help='Limite de crédit du partenaire'
    )

    @api.depends('partner_id')
    def _compute_customer_credit_info(self):
        """Calcule les infos de crédit client."""
        for picking in self:
            if picking.partner_id and picking.picking_type_code == 'outgoing':
                picking.customer_balance = self._get_customer_balance(picking.partner_id)
                picking.partner_credit_limit = picking.partner_id.credit_limit
            else:
                picking.customer_balance = 0.0
                picking.partner_credit_limit = 0.0

    def _get_customer_balance(self, partner):
        """
        Calcul du solde total actuel d'un client.
        Utilise la même logique que le module adi_partner_credit_limit.
        """
        self.env.cr.execute("""
            SELECT id FROM account_account
            WHERE internal_type IN ('receivable', 'payable')
            AND NOT deprecated
        """)
        account_ids = [row[0] for row in self.env.cr.fetchall()]

        if not account_ids:
            return 0.0

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

    def _get_picking_amount(self):
        """
        Calcule le montant total du picking basé sur les commandes de vente liées.
        """
        self.ensure_one()
        amount = 0.0
        if self.sale_id:
            amount = self.sale_id.amount_total
        elif self.origin:
            # Chercher les commandes de vente liées via l'origine
            sale_orders = self.env['sale.order'].search([('name', '=', self.origin)])
            for order in sale_orders:
                amount += order.amount_total
        return amount

    def check_credit_limit_delivery(self):
        """
        Vérifie la limite de crédit du client avant de valider la livraison.
        """
        for picking in self:
            # Vérifier seulement les livraisons sortantes (vers clients)
            if picking.picking_type_code != 'outgoing':
                continue

            partner = picking.partner_id
            if not partner:
                continue

            # Vérifier si la limite de crédit est activée et le mode est 'delivery'
            if partner.credit_limit_active and partner.credit_limit_block_mode == 'delivery':
                total_due = self._get_customer_balance(partner)
                picking_amount = picking._get_picking_amount()
                total_due += picking_amount

                if total_due > partner.credit_limit:
                    raise UserError(_(
                        "La livraison ne peut pas être validée.\n"
                        "Le client '%s' a atteint sa limite de crédit.\n"
                        "Limite de crédit : %.2f\n"
                        "Solde actuel : %.2f\n"
                        "Montant de la livraison : %.2f"
                    ) % (partner.name, partner.credit_limit, total_due - picking_amount, picking_amount))

    def button_validate(self):
        """
        Surcharge de la méthode pour vérifier la limite de crédit avant validation.
        """
        self.check_credit_limit_delivery()
        return super(StockPicking, self).button_validate()
