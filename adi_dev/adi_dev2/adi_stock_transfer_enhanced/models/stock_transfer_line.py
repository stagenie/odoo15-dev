# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockTransferLine(models.Model):
    """
    Extension du modèle adi.stock.transfer.line pour supporter la réservation multi-source.

    Modifications:
    - Calcul de disponibilité incluant les sous-emplacements
    - Traçabilité des emplacements sources utilisés
    - Affichage de la répartition des sources
    """
    _inherit = 'adi.stock.transfer.line'

    # === Nouveau champ: détail des sources ===
    source_line_ids = fields.One2many(
        'adi.stock.transfer.line.source',
        'line_id',
        string='Détail des Sources',
        help="Détail des emplacements sources utilisés pour cette ligne"
    )

    # === Champs calculés pour affichage ===
    source_locations_display = fields.Char(
        compute='_compute_source_display',
        string='Répartition Sources',
        help="Affiche la répartition des quantités par emplacement source"
    )
    source_count = fields.Integer(
        compute='_compute_source_display',
        string='Nb Emplacements'
    )
    has_multi_source = fields.Boolean(
        compute='_compute_source_display',
        string='Multi-Source',
        help="Indique si la ligne utilise plusieurs emplacements sources"
    )

    # === Disponibilité détaillée ===
    availability_detail = fields.Text(
        compute='_compute_availability_detail',
        string='Détail Disponibilité',
        help="Détail de la disponibilité par emplacement"
    )

    @api.depends('source_line_ids', 'source_line_ids.quantity_reserved', 'source_line_ids.location_id')
    def _compute_source_display(self):
        """Calcule l'affichage de la répartition des sources"""
        for line in self:
            if line.source_line_ids:
                parts = []
                for src in line.source_line_ids:
                    loc_name = src.location_id.name or ''
                    qty = src.quantity_reserved or src.quantity_done or 0
                    parts.append(f"{loc_name}: {qty}")
                line.source_locations_display = ' | '.join(parts)
                line.source_count = len(line.source_line_ids)
                line.has_multi_source = len(line.source_line_ids) > 1
            else:
                line.source_locations_display = False
                line.source_count = 0
                line.has_multi_source = False

    @api.depends('product_id', 'transfer_id.source_location_id', 'transfer_id.use_multi_source')
    def _compute_available_quantity(self):
        """
        Surcharge du calcul de disponibilité pour inclure les sous-emplacements.

        Si use_multi_source est activé:
            - Cherche dans l'emplacement source ET tous ses enfants
            - Retourne la somme totale disponible

        Sinon (mode legacy):
            - Comportement original: emplacement strict uniquement
        """
        for line in self:
            if not line.product_id or not line.transfer_id.source_location_id:
                line.available_quantity = 0.0
                continue

            source_location = line.transfer_id.source_location_id

            # Mode multi-source: inclure les sous-emplacements
            if line.transfer_id.use_multi_source:
                # Chercher tous les emplacements enfants (inclus l'emplacement parent)
                child_locations = self.env['stock.location'].search([
                    ('id', 'child_of', source_location.id),
                    ('usage', '=', 'internal')
                ])

                total_available = 0.0
                for loc in child_locations:
                    quants = self.env['stock.quant']._gather(
                        line.product_id,
                        loc,
                        strict=True
                    )
                    # Utiliser available_quantity pour tenir compte des réservations existantes
                    total_available += sum(quants.mapped('available_quantity'))

                line.available_quantity = total_available
            else:
                # Mode legacy: comportement original (emplacement strict)
                quants = self.env['stock.quant']._gather(
                    line.product_id,
                    source_location,
                    strict=True
                )
                line.available_quantity = sum(quants.mapped('quantity'))

    @api.depends('product_id', 'transfer_id.source_location_id', 'transfer_id.use_multi_source')
    def _compute_availability_detail(self):
        """Calcule le détail de disponibilité par emplacement pour affichage informatif"""
        for line in self:
            if not line.product_id or not line.transfer_id.source_location_id:
                line.availability_detail = False
                continue

            if not line.transfer_id.use_multi_source:
                line.availability_detail = False
                continue

            source_location = line.transfer_id.source_location_id

            # Chercher tous les emplacements enfants
            child_locations = self.env['stock.location'].search([
                ('id', 'child_of', source_location.id),
                ('usage', '=', 'internal')
            ], order='complete_name')

            details = []
            for loc in child_locations:
                quants = self.env['stock.quant']._gather(
                    line.product_id,
                    loc,
                    strict=True
                )
                available = sum(quants.mapped('available_quantity'))
                if available > 0:
                    details.append(f"• {loc.complete_name}: {available}")

            line.availability_detail = '\n'.join(details) if details else _("Aucun stock disponible")

    def _check_available_quantity(self):
        """
        Surcharge de la vérification de disponibilité.

        En mode multi-source, vérifie que la quantité totale (incluant sous-emplacements)
        est suffisante. La quantité doit être entièrement disponible (pas de transfert partiel).
        """
        self.ensure_one()

        # Recalculer la disponibilité pour être sûr d'avoir la valeur à jour
        self._compute_available_quantity()

        if self.quantity > self.available_quantity:
            if self.transfer_id.use_multi_source:
                # Message enrichi pour le mode multi-source
                raise ValidationError(_(
                    "Quantité insuffisante pour le produit %(product)s!\n\n"
                    "Quantité demandée: %(requested)s\n"
                    "Quantité disponible (tous emplacements): %(available)s\n\n"
                    "Détail par emplacement:\n%(detail)s"
                ) % {
                    'product': self.product_id.display_name,
                    'requested': self.quantity,
                    'available': self.available_quantity,
                    'detail': self.availability_detail or _("Aucun stock trouvé"),
                })
            else:
                # Message original pour le mode legacy
                raise ValidationError(_(
                    "Quantité insuffisante pour le produit %(product)s!\n"
                    "Quantité demandée: %(requested)s\n"
                    "Quantité disponible: %(available)s"
                ) % {
                    'product': self.product_id.display_name,
                    'requested': self.quantity,
                    'available': self.available_quantity,
                })

    def action_view_source_detail(self):
        """Action pour ouvrir le détail des sources dans une popup"""
        self.ensure_one()
        return {
            'name': _('Détail des Sources - %s') % self.product_id.display_name,
            'type': 'ir.actions.act_window',
            'res_model': 'adi.stock.transfer.line.source',
            'view_mode': 'tree',
            'domain': [('line_id', '=', self.id)],
            'context': {'create': False, 'edit': False},
            'target': 'new',
        }
