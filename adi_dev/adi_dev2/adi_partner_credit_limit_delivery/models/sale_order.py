from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Champ pour afficher l'avertissement de limite de crédit
    credit_limit_warning = fields.Text(
        string='Avertissement limite crédit',
        compute='_compute_credit_limit_warning',
        store=False,
    )
    show_credit_limit_warning = fields.Boolean(
        string='Afficher avertissement',
        compute='_compute_credit_limit_warning',
        store=False,
    )

    @api.depends('partner_id', 'amount_total')
    def _compute_credit_limit_warning(self):
        """Calcule si on doit afficher un avertissement de limite de crédit."""
        for order in self:
            order.show_credit_limit_warning = False
            order.credit_limit_warning = ''

            partner = order.partner_id
            if not partner or not partner.credit_limit_active:
                continue

            # Vérifier si l'option d'avertissement est activée
            if not partner.credit_limit_show_warning:
                continue

            # Calculer le solde
            total_due = self._get_customer_balance(partner)
            total_with_order = total_due + order.amount_total

            # Afficher l'avertissement si le solde dépasse la limite
            if total_with_order > partner.credit_limit:
                order.show_credit_limit_warning = True
                order.credit_limit_warning = _(
                    "⚠️ ATTENTION: Le client '%s' dépasse sa limite de crédit!\n"
                    "Limite: %.2f | Solde actuel: %.2f | Avec cette commande: %.2f"
                ) % (partner.name, partner.credit_limit, total_due, total_with_order)

    def check_credit_limit(self):
        """
        Surcharge pour conditionner le blocage selon le mode choisi.
        Si le mode est 'delivery', on ne bloque pas à la commande.
        """
        for order in self:
            partner = order.partner_id
            # Si le mode de blocage est 'delivery', on saute la vérification à la commande
            if partner.credit_limit_active and partner.credit_limit_block_mode == 'delivery':
                continue
            # Sinon, on appelle la méthode parente pour le blocage à la commande
            super(SaleOrder, order).check_credit_limit()
