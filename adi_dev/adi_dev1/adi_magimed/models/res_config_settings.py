# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # MAGIMED Configuration
    magimed_default_expiration_alert_days = fields.Integer(
        string='Alerte Expiration par Defaut (jours)',
        config_parameter='adi_magimed.default_expiration_alert_days',
        default=30,
        help="Nombre de jours par defaut avant expiration pour l'alerte"
    )
    magimed_default_caution_months = fields.Integer(
        string='Duree Caution par Defaut (mois)',
        config_parameter='adi_magimed.default_caution_months',
        default=24,
        help="Duree par defaut en mois pour les cautions"
    )
    magimed_default_caution_alert_days = fields.Integer(
        string='Alerte Caution par Defaut (jours)',
        config_parameter='adi_magimed.default_caution_alert_days',
        default=30,
        help="Nombre de jours par defaut avant echeance caution pour l'alerte"
    )
    magimed_auto_lot_sequence = fields.Boolean(
        string='Generation Auto Numero de Lot',
        config_parameter='adi_magimed.auto_lot_sequence',
        default=True,
        help="Generer automatiquement les numeros de lot"
    )
    magimed_expiration_email_notification = fields.Boolean(
        string='Notification Email Expiration',
        config_parameter='adi_magimed.expiration_email_notification',
        default=True,
        help="Envoyer des emails pour les alertes d'expiration"
    )
    magimed_caution_email_notification = fields.Boolean(
        string='Notification Email Caution',
        config_parameter='adi_magimed.caution_email_notification',
        default=True,
        help="Envoyer des emails pour les alertes de caution"
    )
