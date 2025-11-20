# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductInventoryReportWizard(models.TransientModel):
    _name = 'product.inventory.report.wizard'
    _description = 'Assistant Rapport Inventaire Produits'

    company_id = fields.Many2one(
        'res.company',
        string='Compagnie',
        default=lambda self: self.env.company.id,
        required=True
    )

    category_ids = fields.Many2many(
        'product.category',
        string='Catégories',
        help='Sélectionner les catégories de produits à inclure. Laisser vide pour toutes les catégories.'
    )

    location_ids = fields.Many2many(
        'stock.location',
        string='Emplacements',
        domain="[('usage', '=', 'internal')]",
        help='Sélectionner les emplacements à afficher. Laisser vide pour tous les emplacements internes.'
    )

    warehouse_ids = fields.Many2many(
        'stock.warehouse',
        string='Entrepôts',
        help='Sélectionner les entrepôts. Laisser vide pour tous les entrepôts.'
    )

    only_available = fields.Boolean(
        string='Uniquement produits en stock',
        default=False,
        help='Afficher uniquement les produits avec stock disponible'
    )

    show_category = fields.Boolean(
        string='Afficher les catégories',
        default=True,
        help='Afficher la colonne catégorie dans le rapport'
    )

    report_type = fields.Selection([
        ('screen', 'Affichage à l\'écran'),
        ('pdf', 'Imprimer PDF'),
    ], string='Type de rapport', default='screen', required=True)

    # Champs pour stocker les informations du rapport (utilisés dans le template PDF)
    report_locations = fields.Char(
        string='Locations',
        default='',
        help='Emplacements séparés par |'
    )
    report_show_category = fields.Boolean(
        string='Show Category',
        default=True
    )

    def action_generate_report(self):
        """Générer le rapport selon les filtres sélectionnés"""
        self.ensure_one()

        # Récupérer les emplacements
        locations = self._get_locations()

        if len(locations) > 10:
            from odoo.exceptions import UserError
            raise UserError("Le nombre d'emplacements ne peut pas dépasser 10. Veuillez affiner vos critères de sélection.")

        # Récupérer les produits selon les filtres
        products = self._get_products()

        # Préparer les données du rapport
        report_lines = self._prepare_report_data(products, locations)

        if self.report_type == 'screen':
            # Créer les lignes de rapport et afficher la vue
            self.env['product.inventory.report.line'].search([]).unlink()

            for line_data in report_lines:
                self.env['product.inventory.report.line'].create(line_data)

            # Créer une vue dynamique avec les noms d'emplacements
            view_id = self._create_dynamic_view(locations)

            return {
                'name': 'Rapport Inventaire Produits',
                'type': 'ir.actions.act_window',
                'res_model': 'product.inventory.report.line',
                'view_mode': 'tree',
                'view_id': view_id,
                'target': 'current',
                'context': {
                    'location_ids': locations.ids,
                    'location_names': locations.mapped('complete_name'),
                    'show_category': self.show_category,
                }
            }
        else:
            # Créer les lignes de rapport dans la base (comme pour screen)
            self.env['product.inventory.report.line'].search([]).unlink()

            for line_data in report_lines:
                self.env['product.inventory.report.line'].create(line_data)

            # Stocker les locations dans le wizard pour les récupérer dans le template
            self.write({
                'report_locations': '|'.join(locations.mapped('complete_name')),
                'report_show_category': self.show_category,
            })

            # Générer le rapport sans passer de data (évite erreur 414 et KeyError)
            return self.env.ref('product_inventory_report.action_report_product_inventory').report_action(self)

    def _create_dynamic_view(self, locations):
        """Créer une vue dynamique avec les noms d'emplacements"""
        # Construire le XML de la vue
        view_arch = '''<?xml version="1.0"?>
        <tree string="Rapport Inventaire Produits" create="false" edit="false" delete="false">
            <field name="default_code" string="Référence"/>
            <field name="name" string="Désignation"/>
            <field name="categ_id" string="Catégorie" invisible="not context.get('show_category', True)"/>'''

        # Ajouter les colonnes pour chaque emplacement
        for i, location in enumerate(locations, 1):
            location_name = location.complete_name or location.name
            view_arch += f'''
            <field name="location_{i}_qty" string="{location_name}"/>'''

        view_arch += '''
            <field name="total_qty" string="Total" sum="Total"/>
        </tree>'''

        # Créer ou mettre à jour la vue
        IrUiView = self.env['ir.ui.view']
        existing_view = IrUiView.search([
            ('model', '=', 'product.inventory.report.line'),
            ('name', '=', 'product.inventory.report.line.tree.dynamic')
        ])

        if existing_view:
            existing_view.write({'arch': view_arch})
            return existing_view.id
        else:
            new_view = IrUiView.create({
                'name': 'product.inventory.report.line.tree.dynamic',
                'model': 'product.inventory.report.line',
                'type': 'tree',
                'arch': view_arch,
            })
            return new_view.id

    def _get_locations(self):
        """Récupérer les emplacements selon les filtres"""
        if self.location_ids:
            return self.location_ids

        domain = [('usage', '=', 'internal')]

        if self.warehouse_ids:
            # Filtrer par entrepôts
            view_location_ids = self.warehouse_ids.mapped('view_location_id').ids
            domain.append(('id', 'child_of', view_location_ids))

        return self.env['stock.location'].search(domain)

    def _get_products(self):
        """Récupérer les produits selon les filtres"""
        domain = [('type', '=', 'product')]  # Uniquement les produits stockables

        if self.category_ids:
            domain.append(('categ_id', 'child_of', self.category_ids.ids))

        return self.env['product.product'].search(domain)

    def _prepare_report_data(self, products, locations):
        """Préparer les données du rapport avec les quantités par emplacement"""
        report_lines = []

        for product in products:
            # Récupérer les quantités par emplacement
            quantities_by_location = {}
            total_qty = 0.0

            for location in locations:
                qty = self.env['stock.quant']._get_available_quantity(
                    product, location
                )
                quantities_by_location[location.id] = qty
                total_qty += qty

            # Filtrer si uniquement produits en stock
            if self.only_available and total_qty <= 0:
                continue

            # Préparer les données de la ligne
            line_data = {
                'product_id': product.id,
                'default_code': product.default_code or '',
                'name': product.name,
                'categ_id': product.categ_id.id if self.show_category else False,
                'total_qty': total_qty,
            }

            # Ajouter les quantités par emplacement
            for i, location in enumerate(locations, 1):
                if i <= 10:  # Limiter à 10 emplacements pour les champs dynamiques
                    line_data[f'location_{i}_qty'] = quantities_by_location.get(location.id, 0.0)

            report_lines.append(line_data)

        return report_lines
