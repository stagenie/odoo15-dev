# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_manually_set = fields.Boolean(
        string='Prix Manuel',
        default=False,
        copy=True,
        help="Indique si le prix unitaire a été modifié manuellement. "
             "Si coché, le prix ne sera pas recalculé lors des modifications de quantité."
    )

    @api.onchange('price_unit')
    def _onchange_price_unit_manual(self):
        """Marque le prix comme manuel quand l'utilisateur le modifie."""
        if self.product_id and self.price_unit:
            # Récupère le prix de la liste de prix pour comparaison
            pricelist_price = self._get_pricelist_price()
            # Si le prix saisi est différent du prix de la liste, on le marque comme manuel
            if pricelist_price and abs(self.price_unit - pricelist_price) > 0.01:
                self.price_manually_set = True

    def _get_pricelist_price(self):
        """Récupère le prix de la liste de prix pour le produit actuel."""
        if not self.product_id or not self.order_id.pricelist_id:
            return 0.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
        )

        return self.order_id.pricelist_id.get_product_price(
            product,
            self.product_uom_qty or 1.0,
            self.order_id.partner_id,
            date=self.order_id.date_order,
            uom_id=self.product_uom.id,
        )

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        """Surcharge pour préserver le prix manuel lors du changement de quantité."""
        if self.price_manually_set and self.price_unit:
            # Sauvegarde le prix actuel
            current_price = self.price_unit
            current_discount = self.discount
            # Appelle la méthode parente
            result = super(SaleOrderLine, self).product_uom_change()
            # Restaure le prix manuel
            self.price_unit = current_price
            self.discount = current_discount
            return result
        return super(SaleOrderLine, self).product_uom_change()

    @api.onchange('discount')
    def _onchange_discount_preserve_price(self):
        """Préserve le prix lors du changement de remise."""
        if self.price_manually_set and self.price_unit:
            # Le prix ne doit pas être modifié lors du changement de remise
            pass

    def write(self, vals):
        """Détecte les modifications manuelles du prix lors de l'enregistrement."""
        for line in self:
            if 'price_unit' in vals and line.product_id:
                pricelist_price = line._get_pricelist_price()
                new_price = vals.get('price_unit', line.price_unit)
                if pricelist_price and abs(new_price - pricelist_price) > 0.01:
                    vals['price_manually_set'] = True
        return super(SaleOrderLine, self).write(vals)

    def action_reset_price_to_pricelist(self):
        """Action pour réinitialiser le prix vers le prix de la liste de prix."""
        for line in self:
            if line.product_id:
                pricelist_price = line._get_pricelist_price()
                line.write({
                    'price_unit': pricelist_price,
                    'price_manually_set': False,
                })
        return True
