# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class AdiMagimedCleanupWizard(models.TransientModel):
    _name = 'adi.magimed.cleanup.wizard'
    _description = 'MAGIMED Cleanup Wizard'

    state = fields.Selection([
        ('step1', 'Etape 1 - Nettoyage orphelins'),
        ('step2', 'Etape 2 - Terminer operations'),
        ('step3', 'Etape 3 - Activer parametres'),
        ('step4', 'Etape 4 - Configurer produits'),
        ('step5', 'Etape 5 - RAZ stock'),
        ('done', 'Termine'),
    ], string='Etat', default='step1', readonly=True)

    log = fields.Text(string='Journal des actions', readonly=True, default='')

    # Compteurs
    orphan_move_line_count = fields.Integer(
        string='Move lines orphelines',
        compute='_compute_counters',
    )
    orphan_move_count = fields.Integer(
        string='Moves orphelins',
        compute='_compute_counters',
    )
    reserved_quant_count = fields.Integer(
        string='Quants avec reservation',
        compute='_compute_counters',
    )
    pending_move_count = fields.Integer(
        string='Moves non termines',
        compute='_compute_counters',
    )
    pending_picking_count = fields.Integer(
        string='Pickings non termines',
        compute='_compute_counters',
    )
    pending_purchase_count = fields.Integer(
        string='Achats non termines',
        compute='_compute_counters',
    )
    pending_sale_count = fields.Integer(
        string='Ventes non terminees',
        compute='_compute_counters',
    )
    lot_tracking_enabled = fields.Boolean(
        string='Suivi par lot active',
        compute='_compute_counters',
    )
    product_expiry_installed = fields.Boolean(
        string='Module product_expiry installe',
        compute='_compute_counters',
    )
    untracked_product_count = fields.Integer(
        string='Produits sans suivi lot',
        compute='_compute_counters',
    )
    no_expiration_product_count = fields.Integer(
        string='Produits sans date expiration',
        compute='_compute_counters',
    )
    no_alert_time_product_count = fields.Integer(
        string='Produits sans delai alerte',
        compute='_compute_counters',
    )
    quant_count = fields.Integer(
        string='Quants existants',
        compute='_compute_counters',
    )

    @api.depends()
    def _compute_counters(self):
        cr = self.env.cr
        for rec in self:
            # Orphan move lines
            cr.execute("""
                SELECT COUNT(*) FROM stock_move_line
                WHERE move_id NOT IN (SELECT id FROM stock_move)
            """)
            rec.orphan_move_line_count = cr.fetchone()[0]

            # Orphan moves
            cr.execute("""
                SELECT COUNT(*) FROM stock_move
                WHERE picking_id IS NOT NULL
                  AND picking_id NOT IN (SELECT id FROM stock_picking)
            """)
            rec.orphan_move_count = cr.fetchone()[0]

            # Reserved quants
            cr.execute("""
                SELECT COUNT(*) FROM stock_quant
                WHERE reserved_quantity != 0
            """)
            rec.reserved_quant_count = cr.fetchone()[0]

            # Pending moves
            cr.execute("""
                SELECT COUNT(*) FROM stock_move
                WHERE state NOT IN ('done', 'cancel')
            """)
            rec.pending_move_count = cr.fetchone()[0]

            # Pending pickings
            cr.execute("""
                SELECT COUNT(*) FROM stock_picking
                WHERE state NOT IN ('done', 'cancel')
            """)
            rec.pending_picking_count = cr.fetchone()[0]

            # Pending purchases
            cr.execute("""
                SELECT COUNT(*) FROM purchase_order
                WHERE state NOT IN ('done', 'purchase', 'cancel')
            """)
            rec.pending_purchase_count = cr.fetchone()[0]

            # Pending sales
            cr.execute("""
                SELECT COUNT(*) FROM sale_order
                WHERE state NOT IN ('done', 'sale', 'cancel')
            """)
            rec.pending_sale_count = cr.fetchone()[0]

            # Lot tracking enabled in settings
            cr.execute("""
                SELECT COUNT(*) FROM res_groups_implied_rel gir
                JOIN ir_model_data imd ON imd.res_id = gir.hid
                WHERE imd.module = 'stock' AND imd.name = 'group_production_lot'
                AND gir.gid = (
                    SELECT res_id FROM ir_model_data
                    WHERE module = 'base' AND name = 'group_user'
                )
            """)
            rec.lot_tracking_enabled = cr.fetchone()[0] > 0

            # Product expiry module installed
            cr.execute("""
                SELECT state FROM ir_module_module
                WHERE name = 'product_expiry'
            """)
            row = cr.fetchone()
            rec.product_expiry_installed = row and row[0] == 'installed'

            # Untracked products
            cr.execute("""
                SELECT COUNT(*) FROM product_template
                WHERE type = 'product' AND (tracking IS NULL OR tracking != 'lot')
            """)
            rec.untracked_product_count = cr.fetchone()[0]

            # Products without use_expiration_date
            cr.execute("""
                SELECT COUNT(*) FROM product_template
                WHERE type = 'product'
                  AND (use_expiration_date IS NULL OR use_expiration_date = False)
            """)
            rec.no_expiration_product_count = cr.fetchone()[0]

            # Products without alert_time
            cr.execute("""
                SELECT COUNT(*) FROM product_template
                WHERE type = 'product'
                  AND (alert_time IS NULL OR alert_time = 0)
            """)
            rec.no_alert_time_product_count = cr.fetchone()[0]

            # Quants
            cr.execute("SELECT COUNT(*) FROM stock_quant")
            rec.quant_count = cr.fetchone()[0]

    def _append_log(self, message):
        now = datetime.now().strftime('%H:%M:%S')
        current_log = self.log or ''
        self.log = current_log + '[%s] %s\n' % (now, message)
        _logger.info('MAGIMED Cleanup: %s', message)

    def _reopen_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_step1_clean_orphans(self):
        """Etape 1 : Nettoyer les enregistrements orphelins"""
        self.ensure_one()
        cr = self.env.cr

        # Move lines orphelines
        cr.execute("""
            DELETE FROM stock_move_line
            WHERE move_id NOT IN (SELECT id FROM stock_move)
        """)
        deleted_ml = cr.rowcount
        self._append_log('Move lines orphelines supprimees : %d' % deleted_ml)

        # Moves orphelins
        cr.execute("""
            DELETE FROM stock_move
            WHERE picking_id IS NOT NULL
              AND picking_id NOT IN (SELECT id FROM stock_picking)
        """)
        deleted_mv = cr.rowcount
        self._append_log('Moves orphelins supprimes : %d' % deleted_mv)

        # Reservations bloquees
        cr.execute("""
            UPDATE stock_quant SET reserved_quantity = 0
            WHERE reserved_quantity != 0
        """)
        updated_q = cr.rowcount
        self._append_log('Quants reservations remises a 0 : %d' % updated_q)

        self.state = 'step2'
        self._append_log('--- Etape 1 terminee ---')
        return self._reopen_wizard()

    def action_step2_close_operations(self):
        """Etape 2 : Terminer toutes les operations"""
        self.ensure_one()
        cr = self.env.cr

        # 2a. Move lines : qty_done = demande + state done
        cr.execute("""
            UPDATE stock_move_line
            SET qty_done = COALESCE(product_uom_qty, 0), state = 'done'
            WHERE state != 'done'
        """)
        ml_count = cr.rowcount
        self._append_log('Move lines terminees : %d' % ml_count)

        # 2b. Moves : forcer state done
        cr.execute("""
            UPDATE stock_move
            SET state = 'done', date = COALESCE(date, NOW())
            WHERE state NOT IN ('done', 'cancel')
        """)
        mv_count = cr.rowcount
        self._append_log('Moves termines : %d' % mv_count)

        # 2c. Pickings : forcer state done
        cr.execute("""
            UPDATE stock_picking
            SET state = 'done', date_done = COALESCE(date_done, NOW())
            WHERE state NOT IN ('done', 'cancel')
        """)
        pk_count = cr.rowcount
        self._append_log('Pickings termines : %d' % pk_count)

        # 2d. Purchase orders / Sale orders : confirmer (pas 'done' = verrouille)
        cr.execute("""
            UPDATE purchase_order SET state = 'purchase'
            WHERE state NOT IN ('done', 'purchase', 'cancel')
        """)
        po_count = cr.rowcount
        self._append_log('Commandes achat confirmees : %d' % po_count)

        cr.execute("""
            UPDATE sale_order SET state = 'sale'
            WHERE state NOT IN ('done', 'sale', 'cancel')
        """)
        so_count = cr.rowcount
        self._append_log('Commandes vente confirmees : %d' % so_count)

        self.state = 'step3'
        self._append_log('--- Etape 2 terminee ---')
        return self._reopen_wizard()

    def action_step3_activate_settings(self):
        """Etape 3 : Activer les parametres Lots & N de serie + product_expiry"""
        self.ensure_one()
        cr = self.env.cr

        # 3a. Activer "Lots & Serial Numbers" (group_stock_production_lot)
        # = ajouter stock.group_production_lot dans les implied_ids de base.group_user
        group_user = self.env.ref('base.group_user')
        group_lot = self.env.ref('stock.group_production_lot')
        if group_lot not in group_user.implied_ids:
            group_user.write({'implied_ids': [(4, group_lot.id)]})
            self._append_log('Parametre "Lots & N de serie" active')
        else:
            self._append_log('Parametre "Lots & N de serie" deja actif')

        # 3b. Installer le module product_expiry si pas installe
        module_expiry = self.env['ir.module.module'].search([
            ('name', '=', 'product_expiry')
        ], limit=1)
        if module_expiry and module_expiry.state != 'installed':
            module_expiry.button_immediate_install()
            self._append_log('Module product_expiry installe')
        else:
            self._append_log('Module product_expiry deja installe')

        self.state = 'step4'
        self._append_log('--- Etape 3 terminee ---')
        return self._reopen_wizard()

    def action_step4_configure_products(self):
        """Etape 4 : Configurer les produits stockables (tracking, expiration, alerte)"""
        self.ensure_one()
        cr = self.env.cr

        # 4a. Activer use_expiration_date sur tous les produits stockables
        cr.execute("""
            UPDATE product_template
            SET use_expiration_date = True
            WHERE type = 'product'
              AND (use_expiration_date IS NULL OR use_expiration_date = False)
        """)
        exp_count = cr.rowcount
        self._append_log('Produits avec expiration activee : %d' % exp_count)

        # 4b. Configurer alert_time = 30 jours par defaut (si pas deja configure)
        cr.execute("""
            UPDATE product_template
            SET alert_time = 30
            WHERE type = 'product'
              AND (alert_time IS NULL OR alert_time = 0)
        """)
        alert_count = cr.rowcount
        self._append_log('Produits avec delai alerte configure (30j) : %d' % alert_count)

        # 4c. Forcer tracking = 'lot' sur tous les produits stockables
        cr.execute("""
            UPDATE product_template
            SET tracking = 'lot'
            WHERE type = 'product'
              AND (tracking IS NULL OR tracking != 'lot')
        """)
        pt_count = cr.rowcount
        self._append_log('Produits passes en suivi par lot : %d' % pt_count)

        self.state = 'step5'
        self._append_log('--- Etape 4 terminee ---')
        return self._reopen_wizard()

    def action_step5_reset_stock(self):
        """Etape 5 : Remettre le stock a zero"""
        self.ensure_one()
        cr = self.env.cr

        cr.execute("DELETE FROM stock_quant")
        q_count = cr.rowcount
        self._append_log('Quants supprimes : %d' % q_count)

        self.state = 'done'
        self._append_log('--- Etape 5 terminee ---')
        self._append_log('=== NETTOYAGE COMPLET TERMINE ===')
        return self._reopen_wizard()
