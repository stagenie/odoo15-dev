# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from collections import defaultdict


class InventoryTrackingInitWizard(models.TransientModel):
    _name = 'inventory.tracking.init.wizard'
    _description = 'Assistant Initialisation Suivi Inventaire'

    date_from = fields.Date(
        string='Date début',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1),
        help="Date de début pour rechercher les mouvements d'inventaire"
    )
    date_to = fields.Date(
        string='Date fin',
        required=True,
        default=fields.Date.today,
        help="Date de fin pour rechercher les mouvements d'inventaire"
    )
    location_ids = fields.Many2many(
        'stock.location',
        string='Emplacements',
        domain="[('usage', '=', 'internal')]",
        help="Laisser vide pour tous les emplacements internes"
    )
    overwrite_existing = fields.Boolean(
        string='Écraser les dates existantes',
        default=False,
        help="Si coché, écrase les dates déjà renseignées. Sinon, ne met à jour que les quants sans date."
    )

    # Champs pour afficher le résultat
    result_message = fields.Text(
        string='Résultat',
        readonly=True
    )
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('done', 'Terminé')
    ], default='draft')

    def action_preview(self):
        """Prévisualiser les mouvements qui seront traités"""
        self.ensure_one()

        moves = self._get_inventory_moves()

        if not moves:
            raise UserError(_("Aucun mouvement d'inventaire trouvé pour la période sélectionnée."))

        # Compter par date
        count_by_date = defaultdict(int)
        for m in moves:
            date_str = m.date.strftime('%Y-%m-%d')
            count_by_date[date_str] += 1

        message = f"Mouvements d'inventaire trouvés : {len(moves)}\n\n"
        message += "Répartition par date :\n"
        for date_str in sorted(count_by_date.keys()):
            message += f"  - {date_str} : {count_by_date[date_str]} mouvements\n"

        # Compter les quants qui seront mis à jour
        quants_to_update = self._get_quants_to_update(moves)
        message += f"\nQuants qui seront mis à jour : {len(quants_to_update)}"

        self.result_message = message

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'inventory.tracking.init.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_initialize(self):
        """Exécuter l'initialisation des dates d'inventaire"""
        self.ensure_one()

        moves = self._get_inventory_moves()

        if not moves:
            raise UserError(_("Aucun mouvement d'inventaire trouvé pour la période sélectionnée."))

        # Regrouper les mouvements par (product_id, location_id) et garder le plus récent
        latest_inventory = {}  # clé: (product_id, location_id) -> {date, user_id}

        for move in moves.sorted(key=lambda m: m.date):
            # Déterminer l'emplacement interne (source ou destination)
            if move.location_id.usage == 'internal':
                location = move.location_id
            elif move.location_dest_id.usage == 'internal':
                location = move.location_dest_id
            else:
                continue

            key = (move.product_id.id, location.id)
            # On prend toujours le plus récent (le tri est ascendant, donc le dernier écrase)
            latest_inventory[key] = {
                'date': move.date.date(),
                'user_id': move.write_uid.id or move.create_uid.id,
            }

        # Mettre à jour les quants
        updated_count = 0
        not_found_count = 0

        for (product_id, location_id), info in latest_inventory.items():
            quant = self.env['stock.quant'].search([
                ('product_id', '=', product_id),
                ('location_id', '=', location_id),
            ], limit=1)

            if quant:
                # Vérifier si on doit mettre à jour
                if self.overwrite_existing or not quant.last_inventory_date:
                    quant.sudo().write({
                        'last_inventory_date': info['date'],
                        'last_inventory_user_id': info['user_id'],
                    })
                    updated_count += 1
            else:
                not_found_count += 1

        self.result_message = _(
            "Initialisation terminée !\n\n"
            "- Mouvements d'inventaire analysés : %d\n"
            "- Combinaisons produit/emplacement trouvées : %d\n"
            "- Quants mis à jour : %d\n"
            "- Quants non trouvés (produit plus en stock) : %d"
        ) % (len(moves), len(latest_inventory), updated_count, not_found_count)

        self.state = 'done'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'inventory.tracking.init.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _get_inventory_moves(self):
        """Récupérer les mouvements d'inventaire pour la période"""
        domain = [
            ('is_inventory', '=', True),
            ('state', '=', 'done'),
            ('date', '>=', self.date_from),
            ('date', '<=', fields.Datetime.to_datetime(self.date_to).replace(hour=23, minute=59, second=59)),
        ]

        if self.location_ids:
            domain.append('|')
            domain.append(('location_id', 'in', self.location_ids.ids))
            domain.append(('location_dest_id', 'in', self.location_ids.ids))

        return self.env['stock.move'].search(domain, order='date asc')

    def _get_quants_to_update(self, moves):
        """Compter les quants qui seront mis à jour"""
        product_location_pairs = set()

        for move in moves:
            if move.location_id.usage == 'internal':
                product_location_pairs.add((move.product_id.id, move.location_id.id))
            if move.location_dest_id.usage == 'internal':
                product_location_pairs.add((move.product_id.id, move.location_dest_id.id))

        # Chercher les quants correspondants
        quants = self.env['stock.quant']
        for product_id, location_id in product_location_pairs:
            domain = [
                ('product_id', '=', product_id),
                ('location_id', '=', location_id),
            ]
            if not self.overwrite_existing:
                domain.append(('last_inventory_date', '=', False))
            quants |= self.env['stock.quant'].search(domain, limit=1)

        return quants

    def action_back(self):
        """Retourner à l'état brouillon"""
        self.state = 'draft'
        self.result_message = False
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'inventory.tracking.init.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
