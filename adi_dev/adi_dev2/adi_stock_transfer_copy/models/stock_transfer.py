# -*- coding: utf-8 -*-
import json
from odoo import models, fields, api, _


class StockTransferCopy(models.Model):
    _inherit = 'adi.stock.transfer'

    product_counts_json = fields.Char(default='{}', copy=False)

    @api.onchange('transfer_line_ids')
    def _onchange_transfer_line_duplicate_warning(self):
        if not self.transfer_line_ids:
            self.product_counts_json = '{}'
            return

        # Compter les occurrences actuelles de chaque produit
        current_counts = {}
        for line in self.transfer_line_ids:
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
            for line in self.transfer_line_ids:
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

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'source_picking_id': False,
            'dest_picking_id': False,
            'transit_location_id': False,
            'transfer_line_ids': [],  # Prevent default One2many copy (may fail silently)
        })
        new_transfer = super().copy(default=default)
        # Explicitly copy lines with reset quantities
        for line in self.transfer_line_ids:
            line.copy(default={
                'transfer_id': new_transfer.id,
                'qty_sent': 0.0,
                'qty_received': 0.0,
            })
        return new_transfer
