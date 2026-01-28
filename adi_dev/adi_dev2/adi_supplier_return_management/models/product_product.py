# -*- coding: utf-8 -*-
from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Surcharge de name_search pour filtrer les produits dans le contexte des retours fournisseurs.

        Si le contexte contient 'supplier_return_partner_id' et 'supplier_return_origin_mode',
        on filtre les produits selon le mode d'origine.
        """
        args = args or []

        # Vérifier si on est dans un contexte de retour fournisseur
        supplier_partner_id = self._context.get('supplier_return_partner_id')
        supplier_origin_mode = self._context.get('supplier_return_origin_mode')
        supplier_picking_ids = self._context.get('supplier_return_picking_ids')

        if supplier_partner_id and supplier_origin_mode:

            if supplier_origin_mode == 'strict' and supplier_picking_ids:
                # Mode strict : produits des BR sélectionnés uniquement
                pickings = self.env['stock.picking'].browse(supplier_picking_ids)
                move_lines = pickings.mapped('move_line_ids')
                allowed_product_ids = move_lines.mapped('product_id').ids
                if allowed_product_ids:
                    args = args + [('id', 'in', allowed_product_ids)]
                else:
                    return []

            elif supplier_origin_mode == 'flexible':
                # Mode souple : produits déjà reçus du fournisseur
                received_pickings = self.env['stock.picking'].search([
                    ('partner_id', '=', supplier_partner_id),
                    ('state', '=', 'done'),
                    ('picking_type_code', '=', 'incoming')
                ])
                if received_pickings:
                    move_lines = received_pickings.mapped('move_line_ids')
                    allowed_product_ids = move_lines.mapped('product_id').ids
                    if allowed_product_ids:
                        args = args + [('id', 'in', allowed_product_ids)]
                    else:
                        return []
                else:
                    return []

        return super().name_search(name=name, args=args, operator=operator, limit=limit)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """
        Surcharge de search_read pour filtrer les produits dans la recherche avancée (fournisseurs).
        """
        domain = domain or []

        # Vérifier si on est dans un contexte de retour fournisseur
        supplier_partner_id = self._context.get('supplier_return_partner_id')
        supplier_origin_mode = self._context.get('supplier_return_origin_mode')
        supplier_picking_ids = self._context.get('supplier_return_picking_ids')

        if supplier_partner_id and supplier_origin_mode:

            if supplier_origin_mode == 'strict' and supplier_picking_ids:
                pickings = self.env['stock.picking'].browse(supplier_picking_ids)
                move_lines = pickings.mapped('move_line_ids')
                allowed_product_ids = move_lines.mapped('product_id').ids
                if allowed_product_ids:
                    domain = domain + [('id', 'in', allowed_product_ids)]
                else:
                    domain = [('id', '=', False)]

            elif supplier_origin_mode == 'flexible':
                received_pickings = self.env['stock.picking'].search([
                    ('partner_id', '=', supplier_partner_id),
                    ('state', '=', 'done'),
                    ('picking_type_code', '=', 'incoming')
                ])
                if received_pickings:
                    move_lines = received_pickings.mapped('move_line_ids')
                    allowed_product_ids = move_lines.mapped('product_id').ids
                    if allowed_product_ids:
                        domain = domain + [('id', 'in', allowed_product_ids)]
                    else:
                        domain = [('id', '=', False)]
                else:
                    domain = [('id', '=', False)]

        return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
