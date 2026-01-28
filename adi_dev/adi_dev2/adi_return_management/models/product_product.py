# -*- coding: utf-8 -*-
from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Surcharge de name_search pour filtrer les produits dans le contexte des retours clients.

        Si le contexte contient 'return_partner_id' et 'return_origin_mode',
        on filtre les produits selon le mode d'origine.
        """
        args = args or []

        # Vérifier si on est dans un contexte de retour client
        return_partner_id = self._context.get('return_partner_id')
        return_origin_mode = self._context.get('return_origin_mode')
        return_picking_ids = self._context.get('return_picking_ids')

        if return_partner_id and return_origin_mode:

            if return_origin_mode == 'strict' and return_picking_ids:
                # Mode strict : produits des BL sélectionnés uniquement
                pickings = self.env['stock.picking'].browse(return_picking_ids)
                move_lines = pickings.mapped('move_line_ids')
                allowed_product_ids = move_lines.mapped('product_id').ids
                if allowed_product_ids:
                    args = args + [('id', 'in', allowed_product_ids)]
                else:
                    # Aucun produit autorisé, retourner liste vide
                    return []

            elif return_origin_mode == 'flexible':
                # Mode souple : produits déjà livrés au client
                delivered_pickings = self.env['stock.picking'].search([
                    ('partner_id', '=', return_partner_id),
                    ('state', '=', 'done'),
                    ('picking_type_code', '=', 'outgoing')
                ])
                if delivered_pickings:
                    move_lines = delivered_pickings.mapped('move_line_ids')
                    allowed_product_ids = move_lines.mapped('product_id').ids
                    if allowed_product_ids:
                        args = args + [('id', 'in', allowed_product_ids)]
                    else:
                        return []
                else:
                    # Aucune livraison trouvée, retourner liste vide
                    return []

            # Mode 'none' : pas de filtrage, comportement par défaut

        return super().name_search(name=name, args=args, operator=operator, limit=limit)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """
        Surcharge de search_read pour filtrer les produits dans la recherche avancée.
        """
        domain = domain or []

        # Vérifier si on est dans un contexte de retour client
        return_partner_id = self._context.get('return_partner_id')
        return_origin_mode = self._context.get('return_origin_mode')
        return_picking_ids = self._context.get('return_picking_ids')

        if return_partner_id and return_origin_mode:

            if return_origin_mode == 'strict' and return_picking_ids:
                pickings = self.env['stock.picking'].browse(return_picking_ids)
                move_lines = pickings.mapped('move_line_ids')
                allowed_product_ids = move_lines.mapped('product_id').ids
                if allowed_product_ids:
                    domain = domain + [('id', 'in', allowed_product_ids)]
                else:
                    domain = [('id', '=', False)]

            elif return_origin_mode == 'flexible':
                delivered_pickings = self.env['stock.picking'].search([
                    ('partner_id', '=', return_partner_id),
                    ('state', '=', 'done'),
                    ('picking_type_code', '=', 'outgoing')
                ])
                if delivered_pickings:
                    move_lines = delivered_pickings.mapped('move_line_ids')
                    allowed_product_ids = move_lines.mapped('product_id').ids
                    if allowed_product_ids:
                        domain = domain + [('id', 'in', allowed_product_ids)]
                    else:
                        domain = [('id', '=', False)]
                else:
                    domain = [('id', '=', False)]

        return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
