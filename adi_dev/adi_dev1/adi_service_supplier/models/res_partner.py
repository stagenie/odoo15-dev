# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_service_supplier = fields.Boolean(
        string='Fournisseur de Service',
        default=False,
        help="Cocher si ce fournisseur est un fournisseur de service (prestataire)."
    )

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        """Surcharge pour filtrer les fournisseurs de service selon le contexte."""
        args = args or []
        context = self._context or {}

        # Si le contexte demande uniquement les fournisseurs de service
        if context.get('service_supplier_only'):
            args = args + [('is_service_supplier', '=', True)]

        return super(ResPartner, self)._name_search(
            name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid
        )
