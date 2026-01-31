# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SupplierReturnOrderAddProductsWizard(models.TransientModel):
    _name = 'supplier.return.order.add.products.wizard'
    _description = 'Assistant ajout produits retour fournisseur'

    return_order_id = fields.Many2one(
        'supplier.return.order',
        string='Ordre de retour',
        required=True,
        readonly=True
    )

    partner_id = fields.Many2one(
        related='return_order_id.partner_id',
        string='Fournisseur'
    )

    origin_mode = fields.Selection(
        related='return_order_id.origin_mode',
        string='Mode origine'
    )

    line_ids = fields.One2many(
        'supplier.return.order.add.products.line',
        'wizard_id',
        string='Produits disponibles'
    )

    search_filter = fields.Char(
        string='Rechercher',
        help="Rechercher par reference ou nom de produit"
    )

    filter_count = fields.Integer(
        string='Resultats',
        compute='_compute_filter_count'
    )

    @api.depends('search_filter', 'line_ids', 'line_ids.match_filter')
    def _compute_filter_count(self):
        for wizard in self:
            if wizard.search_filter:
                wizard.filter_count = len(wizard.line_ids.filtered(lambda l: l.match_filter))
            else:
                wizard.filter_count = len(wizard.line_ids)

    @api.onchange('search_filter')
    def _onchange_search_filter(self):
        """Met a jour le filtre de correspondance sur les lignes"""
        search_term = (self.search_filter or '').strip().lower()
        for line in self.line_ids:
            if not search_term:
                line.match_filter = True
            else:
                # Recherche dans reference et nom du produit
                ref = (line.product_id.default_code or '').lower()
                name = (line.product_id.name or '').lower()
                line.match_filter = search_term in ref or search_term in name

    def action_apply_filter(self):
        """Applique le filtre de recherche"""
        self._onchange_search_filter()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.model
    def default_get(self, fields_list):
        """Charge les produits disponibles selon le mode d'origine"""
        res = super().default_get(fields_list)

        # Recuperer l'ordre de retour actif
        return_order_id = self._context.get('active_id')
        if not return_order_id:
            return res

        return_order = self.env['supplier.return.order'].browse(return_order_id)
        res['return_order_id'] = return_order_id

        # Recuperer les produits deja dans l'ordre de retour
        existing_product_ids = return_order.line_ids.mapped('product_id').ids

        # Calculer les produits disponibles selon le mode
        available_products = self._get_available_products(return_order)

        # Creer les lignes du wizard
        lines = []
        for product_data in available_products:
            # Ne pas afficher les produits deja ajoutes
            if product_data['product_id'] in existing_product_ids:
                continue

            lines.append((0, 0, {
                'product_id': product_data['product_id'],
                'qty_received': product_data['qty_received'],
                'price_unit': product_data['price_unit'],
                'picking_id': product_data.get('picking_id'),
                'purchase_line_id': product_data.get('purchase_line_id'),
                'selected': False,
                'match_filter': True,
            }))

        res['line_ids'] = lines
        return res

    def _get_available_products(self, return_order):
        """
        Retourne la liste des produits disponibles pour le retour.

        Retourne une liste de dictionnaires avec:
        - product_id: ID du produit
        - qty_received: Quantite recue
        - price_unit: Prix d'achat
        - picking_id: ID du BR (optionnel)
        - purchase_line_id: ID de la ligne d'achat (optionnel)
        """
        products = []
        partner = return_order.partner_id
        origin_mode = return_order.origin_mode

        if origin_mode == 'strict' and return_order.picking_ids:
            # Mode strict: produits des BR selectionnes
            for picking in return_order.picking_ids:
                for move_line in picking.move_line_ids:
                    product = move_line.product_id
                    # Chercher le prix dans la commande d'achat
                    price = product.standard_price
                    purchase_line = False
                    if picking.purchase_id:
                        purchase_lines = picking.purchase_id.order_line.filtered(
                            lambda l: l.product_id == product
                        )
                        if purchase_lines:
                            purchase_line = purchase_lines[0]
                            price = purchase_line.price_unit

                    # Verifier si le produit existe deja dans la liste
                    existing = next((p for p in products if p['product_id'] == product.id), None)
                    if existing:
                        existing['qty_received'] += move_line.qty_done
                    else:
                        products.append({
                            'product_id': product.id,
                            'qty_received': move_line.qty_done,
                            'price_unit': price,
                            'picking_id': picking.id,
                            'purchase_line_id': purchase_line.id if purchase_line else False,
                        })

        elif origin_mode == 'flexible' and partner:
            # Mode souple: tous les produits recus du fournisseur
            received_pickings = self.env['stock.picking'].search([
                ('partner_id', '=', partner.id),
                ('state', '=', 'done'),
                ('picking_type_code', '=', 'incoming')
            ], order='date_done desc')

            for picking in received_pickings:
                for move_line in picking.move_line_ids:
                    product = move_line.product_id

                    # Chercher le prix dans la commande d'achat
                    price = product.standard_price
                    purchase_line = False
                    if picking.purchase_id:
                        purchase_lines = picking.purchase_id.order_line.filtered(
                            lambda l: l.product_id == product
                        )
                        if purchase_lines:
                            purchase_line = purchase_lines[0]
                            price = purchase_line.price_unit

                    # Verifier si le produit existe deja dans la liste
                    existing = next((p for p in products if p['product_id'] == product.id), None)
                    if existing:
                        existing['qty_received'] += move_line.qty_done
                    else:
                        products.append({
                            'product_id': product.id,
                            'qty_received': move_line.qty_done,
                            'price_unit': price,
                            'picking_id': picking.id,
                            'purchase_line_id': purchase_line.id if purchase_line else False,
                        })

        else:
            # Mode libre: tous les produits stockables
            all_products = self.env['product.product'].search([
                ('type', 'in', ['product', 'consu'])
            ], limit=500)
            for product in all_products:
                products.append({
                    'product_id': product.id,
                    'qty_received': 0,
                    'price_unit': product.standard_price,
                    'picking_id': False,
                    'purchase_line_id': False,
                })

        return products

    def action_add_products(self):
        """Ajoute les produits selectionnes a l'ordre de retour"""
        self.ensure_one()

        selected_lines = self.line_ids.filtered(lambda l: l.selected)
        if not selected_lines:
            raise UserError(_("Veuillez selectionner au moins un produit."))

        # Verifier le controle de quantite si active
        check_qty = self.env['ir.config_parameter'].sudo().get_param(
            'adi_supplier_return_management.return_check_qty_exceeded', 'True'
        )
        if check_qty in ('True', 'true', '1', True):
            for line in selected_lines:
                if line.qty_received > 0 and line.qty_to_return > line.qty_received:
                    raise UserError(_(
                        "La quantite a retourner (%.2f) pour '%s' depasse la quantite recue (%.2f)."
                    ) % (line.qty_to_return, line.product_id.display_name, line.qty_received))

        return_order = self.return_order_id

        for line in selected_lines:
            # Creer la ligne de retour
            vals = {
                'return_order_id': return_order.id,
                'product_id': line.product_id.id,
                'qty_returned': line.qty_to_return or 1.0,
                'price_unit': line.price_unit,
            }

            # Ajouter le lien vers la ligne d'achat si disponible
            if line.purchase_line_id:
                vals['purchase_line_id'] = line.purchase_line_id.id

            # Ajouter le lien vers le BR d'origine si disponible
            if line.picking_id:
                vals['origin_picking_id'] = line.picking_id.id

            self.env['supplier.return.order.line'].create(vals)

        return {'type': 'ir.actions.act_window_close'}

    def action_select_all(self):
        """Selectionne tous les produits (filtres si recherche active)"""
        lines_to_select = self.line_ids.filtered(lambda l: l.match_filter)
        lines_to_select.write({'selected': True})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_deselect_all(self):
        """Deselectionne tous les produits (filtres si recherche active)"""
        lines_to_deselect = self.line_ids.filtered(lambda l: l.match_filter)
        lines_to_deselect.write({'selected': False})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_clear_filter(self):
        """Efface le filtre de recherche"""
        self.search_filter = False
        self.line_ids.write({'match_filter': True})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }


class SupplierReturnOrderAddProductsLine(models.TransientModel):
    _name = 'supplier.return.order.add.products.line'
    _description = 'Ligne assistant ajout produits fournisseur'
    _order = 'match_filter desc, id'

    wizard_id = fields.Many2one(
        'supplier.return.order.add.products.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )

    selected = fields.Boolean(
        string='Selectionner',
        default=False
    )

    match_filter = fields.Boolean(
        string='Correspond au filtre',
        default=True
    )

    product_id = fields.Many2one(
        'product.product',
        string='Produit',
        required=True
    )

    default_code = fields.Char(
        related='product_id.default_code',
        string='Reference'
    )

    qty_received = fields.Float(
        string='Qte recue',
        help="Quantite totale recue du fournisseur"
    )

    qty_to_return = fields.Float(
        string='Qte a retourner',
        default=1.0
    )

    price_unit = fields.Float(
        string='Prix unitaire'
    )

    picking_id = fields.Many2one(
        'stock.picking',
        string='BR origine'
    )

    purchase_line_id = fields.Many2one(
        'purchase.order.line',
        string='Ligne achat'
    )

    purchase_order_id = fields.Many2one(
        related='purchase_line_id.order_id',
        string='Commande',
        store=False
    )
