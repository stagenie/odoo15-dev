# -*- coding: utf-8 -*-
"""
Configuration des paramètres d'affichage des soldes rapprochés
"""

from odoo import models, fields, api


class TreasuryConfigReconciliation(models.Model):
    """
    Modèle singleton pour stocker la configuration du rapprochement.
    Utilise un singleton car ir.config_parameter ne supporte pas les booléens directement.
    """
    _name = 'treasury.config.reconciliation'
    _description = 'Configuration Affichage Rapprochement'

    name = fields.Char(default='Configuration Rapprochement', readonly=True)
    show_reconciliation_details = fields.Boolean(
        string='Afficher les détails de rapprochement',
        default=True,
        help="Si activé, affiche les soldes rapprochés et non rapprochés "
             "dans le tableau de bord et les vues des banques"
    )

    @api.model
    def get_config(self):
        """Récupère ou crée la configuration singleton"""
        config = self.search([], limit=1)
        if not config:
            config = self.create({'name': 'Configuration Rapprochement'})
        return config

    @api.model
    def get_show_reconciliation_details(self):
        """Retourne la valeur du paramètre d'affichage"""
        config = self.get_config()
        return config.show_reconciliation_details


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    treasury_show_reconciliation_details = fields.Boolean(
        string='Afficher les détails de rapprochement',
        help="Affiche les soldes rapprochés et non rapprochés dans le tableau de bord "
             "et les vues des banques",
        config_parameter='treasury.show_reconciliation_details'
    )

    def set_values(self):
        """Sauvegarde les valeurs dans le modèle de configuration"""
        super(ResConfigSettings, self).set_values()
        config = self.env['treasury.config.reconciliation'].get_config()
        config.write({
            'show_reconciliation_details': self.treasury_show_reconciliation_details
        })

    @api.model
    def get_values(self):
        """Récupère les valeurs depuis le modèle de configuration"""
        res = super(ResConfigSettings, self).get_values()
        config = self.env['treasury.config.reconciliation'].get_config()
        res.update({
            'treasury_show_reconciliation_details': config.show_reconciliation_details
        })
        return res
