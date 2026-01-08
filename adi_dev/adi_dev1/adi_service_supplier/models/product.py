# -*- coding: utf-8 -*-

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        """Surcharge pour filtrer les produits de type service selon le contexte."""
        args = args or []
        context = self._context or {}

        # Si le contexte demande uniquement les produits de type service
        if context.get('service_products_only'):
            args = args + [('type', '=', 'service')]

        return super(ProductProduct, self)._name_search(
            name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid
        )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        """Surcharge pour filtrer les produits de type service selon le contexte."""
        args = args or []
        context = self._context or {}

        # Si le contexte demande uniquement les produits de type service
        if context.get('service_products_only'):
            args = args + [('type', '=', 'service')]

        return super(ProductTemplate, self)._name_search(
            name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid
        )
