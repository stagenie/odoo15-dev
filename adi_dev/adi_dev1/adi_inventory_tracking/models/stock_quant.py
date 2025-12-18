# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date, timedelta


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    last_inventory_date = fields.Date(
        string='Date dernier inventaire',
        readonly=True,
        help="Date à laquelle cet article a été inventorié pour la dernière fois dans cet emplacement"
    )
    last_inventory_user_id = fields.Many2one(
        'res.users',
        string='Inventorié par',
        readonly=True,
        help="Utilisateur qui a effectué le dernier inventaire de cet article"
    )
    days_since_inventory = fields.Integer(
        string='Jours depuis inventaire',
        compute='_compute_days_since_inventory',
        store=False,
        help="Nombre de jours depuis le dernier inventaire"
    )
    inventory_status = fields.Selection([
        ('never', 'Jamais inventorié'),
        ('recent', 'Récent (< 7 jours)'),
        ('month', 'Ce mois'),
        ('old', 'Ancien (> 30 jours)'),
    ], string='Statut inventaire',
        compute='_compute_inventory_status',
        store=False,
        help="Statut basé sur la date du dernier inventaire"
    )

    @api.depends('last_inventory_date')
    def _compute_days_since_inventory(self):
        today = date.today()
        for quant in self:
            if quant.last_inventory_date:
                quant.days_since_inventory = (today - quant.last_inventory_date).days
            else:
                quant.days_since_inventory = -1  # -1 = jamais inventorié

    @api.depends('last_inventory_date')
    def _compute_inventory_status(self):
        today = date.today()
        for quant in self:
            if not quant.last_inventory_date:
                quant.inventory_status = 'never'
            else:
                days = (today - quant.last_inventory_date).days
                if days < 7:
                    quant.inventory_status = 'recent'
                elif days <= 30:
                    quant.inventory_status = 'month'
                else:
                    quant.inventory_status = 'old'

    def _apply_inventory(self):
        """
        Override pour enregistrer la date et l'utilisateur du dernier inventaire
        avant que les champs ne soient réinitialisés.
        """
        # Sauvegarder les informations d'inventaire AVANT l'application
        inventory_info = {}
        for quant in self:
            # On vérifie si une quantité a été saisie (inventory_quantity_set)
            if quant.inventory_quantity_set:
                inventory_info[quant.id] = {
                    'last_inventory_date': fields.Date.today(),
                    'last_inventory_user_id': quant.user_id.id or self.env.user.id,
                }

        # Appeler la méthode parente
        result = super(StockQuant, self)._apply_inventory()

        # Mettre à jour les champs de suivi d'inventaire
        for quant_id, info in inventory_info.items():
            quant = self.browse(quant_id)
            quant.sudo().write({
                'last_inventory_date': info['last_inventory_date'],
                'last_inventory_user_id': info['last_inventory_user_id'],
            })

        return result
