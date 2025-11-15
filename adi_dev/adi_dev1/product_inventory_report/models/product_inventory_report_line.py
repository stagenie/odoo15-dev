# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductInventoryReportLine(models.TransientModel):
    _name = 'product.inventory.report.line'
    _description = 'Ligne Rapport Inventaire Produit'
    _order = 'default_code, name'

    product_id = fields.Many2one('product.product', string='Produit', readonly=True)
    default_code = fields.Char(string='Référence', readonly=True)
    name = fields.Char(string='Désignation', readonly=True)
    categ_id = fields.Many2one('product.category', string='Catégorie', readonly=True)
    total_qty = fields.Float(string='Total', readonly=True, digits='Product Unit of Measure')

    # Champs dynamiques pour les emplacements (jusqu'à 10 emplacements)
    location_1_qty = fields.Float(string='Emplacement 1', readonly=True, digits='Product Unit of Measure')
    location_2_qty = fields.Float(string='Emplacement 2', readonly=True, digits='Product Unit of Measure')
    location_3_qty = fields.Float(string='Emplacement 3', readonly=True, digits='Product Unit of Measure')
    location_4_qty = fields.Float(string='Emplacement 4', readonly=True, digits='Product Unit of Measure')
    location_5_qty = fields.Float(string='Emplacement 5', readonly=True, digits='Product Unit of Measure')
    location_6_qty = fields.Float(string='Emplacement 6', readonly=True, digits='Product Unit of Measure')
    location_7_qty = fields.Float(string='Emplacement 7', readonly=True, digits='Product Unit of Measure')
    location_8_qty = fields.Float(string='Emplacement 8', readonly=True, digits='Product Unit of Measure')
    location_9_qty = fields.Float(string='Emplacement 9', readonly=True, digits='Product Unit of Measure')
    location_10_qty = fields.Float(string='Emplacement 10', readonly=True, digits='Product Unit of Measure')
