# -*- coding: utf-8 -*-
import json
from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Champ pour memoriser le comptage des produits (doit etre dans la vue)
    product_counts_json = fields.Char(default='{}', copy=False)

    @api.onchange('move_ids_without_package')
    def _onchange_move_ids_duplicate_warning(self):
        """Alerte quand on ajoute un article qui existe deja"""
        if not self.move_ids_without_package:
            self.product_counts_json = '{}'
            return

        # Compter les occurrences actuelles de chaque produit
        current_counts = {}
        for line in self.move_ids_without_package:
            if line.product_id:
                pid = line.product_id.id
                current_counts[pid] = current_counts.get(pid, 0) + 1

        # Recuperer les comptages precedents
        try:
            previous_counts = json.loads(self.product_counts_json or '{}')
        except (json.JSONDecodeError, TypeError):
            previous_counts = {}

        # Trouver les produits dont le count a augmente ET qui sont > 1
        new_duplicate_ids = []
        for pid, count in current_counts.items():
            prev_count = previous_counts.get(str(pid), 0)
            if count > prev_count and count > 1:
                new_duplicate_ids.append(pid)

        # Mettre a jour les comptages
        self.product_counts_json = json.dumps({str(k): v for k, v in current_counts.items()})

        if new_duplicate_ids:
            duplicate_names = []
            for line in self.move_ids_without_package:
                if line.product_id.id in new_duplicate_ids:
                    duplicate_names.append(line.product_id.display_name)
                    new_duplicate_ids.remove(line.product_id.id)

            if duplicate_names:
                return {
                    'warning': {
                        'title': _('Article en double !'),
                        'message': _(
                            'Attention : L\'article "%s" existe deja dans ce document !'
                        ) % duplicate_names[0] if len(duplicate_names) == 1 else _(
                            'Attention : Les articles suivants existent deja :\n%s'
                        ) % '\n'.join('- ' + name for name in duplicate_names)
                    }
                }
