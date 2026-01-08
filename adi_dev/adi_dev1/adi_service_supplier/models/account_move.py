# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_service_invoice = fields.Boolean(
        string='Facture Service',
        default=False,
        help="Cocher pour indiquer que cette facture est une facture de service. "
             "Cela filtrera les fournisseurs et les articles pour n'afficher que les services."
    )

    @api.onchange('is_service_invoice')
    def _onchange_is_service_invoice(self):
        """Vider le fournisseur si on change le type de facture et qu'il ne correspond pas."""
        if self.is_service_invoice and self.partner_id and not self.partner_id.is_service_supplier:
            self.partner_id = False
        elif not self.is_service_invoice and self.partner_id and self.partner_id.is_service_supplier:
            # Optionnel: garder le fournisseur même s'il est de type service
            pass


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_id_service_check(self):
        """Avertir si le produit n'est pas un service sur une facture service."""
        if (self.move_id.is_service_invoice and
            self.product_id and
            self.product_id.type != 'service'):
            return {
                'warning': {
                    'title': 'Attention',
                    'message': "Cet article n'est pas un service. Sur une facture service, "
                               "il est recommandé d'utiliser uniquement des articles de type 'Service'."
                }
            }
