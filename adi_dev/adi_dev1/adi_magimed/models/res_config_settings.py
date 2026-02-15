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

    # Lot Duplicate Control
    magimed_lot_duplicate_action = fields.Selection([
        ('warn', 'Avertissement uniquement'),
        ('block', 'Bloquer la creation'),
        ('update', 'Utiliser le lot existant'),
    ], string='Action Doublon Lot Reception',
       config_parameter='adi_magimed.lot_duplicate_action',
       default='warn')

    # Expiry Control on Validation
    magimed_expiry_control_mode = fields.Selection([
        ('block', 'Bloquer la validation'),
        ('warn', 'Avertissement (confirmer pour continuer)'),
        ('none', 'Aucun controle'),
    ], string='Controle Expiration Validation',
       config_parameter='adi_magimed.expiry_control_mode',
       default='block')

    magimed_expiry_check_days = fields.Integer(
        string='Seuil jours expiration',
        config_parameter='adi_magimed.expiry_check_days',
        default=0,
        help="Bloquer/alerter si lot expire dans X jours (0 = uniquement lots deja expires)"
    )
