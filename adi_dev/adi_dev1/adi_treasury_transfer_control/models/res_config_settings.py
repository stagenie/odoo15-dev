# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # =========================================================================
    # PARAMÈTRES DE CONTRÔLE DES TRANSFERTS
    # =========================================================================

    transfer_control_enabled = fields.Boolean(
        string='Activer le contrôle des transferts',
        config_parameter='adi_treasury_transfer_control.control_enabled',
        default=True,
        help="Activer les vérifications de solde avant les transferts"
    )

    transfer_require_check = fields.Boolean(
        string='Contrôle obligatoire',
        config_parameter='adi_treasury_transfer_control.require_check',
        default=True,
        help="Exiger un contrôle manuel avant chaque confirmation de transfert"
    )

    transfer_auto_check = fields.Boolean(
        string='Contrôle automatique',
        config_parameter='adi_treasury_transfer_control.auto_check',
        default=True,
        help="Effectuer automatiquement le contrôle lors de la confirmation"
    )

    transfer_block_insufficient = fields.Boolean(
        string='Bloquer si solde insuffisant',
        config_parameter='adi_treasury_transfer_control.block_insufficient',
        default=True,
        help="Bloquer les transferts si le solde source est insuffisant"
    )

    transfer_block_overdraft = fields.Boolean(
        string='Bloquer si découvert dépassé',
        config_parameter='adi_treasury_transfer_control.block_overdraft',
        default=True,
        help="Bloquer les transferts bancaires si le découvert serait dépassé"
    )

    transfer_block_capacity = fields.Boolean(
        string='Bloquer si capacité dépassée',
        config_parameter='adi_treasury_transfer_control.block_capacity',
        default=True,
        help="Bloquer les transferts si la capacité de la destination serait dépassée"
    )

    transfer_allow_manager_force = fields.Boolean(
        string='Autoriser les managers à forcer',
        config_parameter='adi_treasury_transfer_control.allow_manager_force',
        default=True,
        help="Permettre aux managers de forcer les transferts malgré les erreurs"
    )

    transfer_log_controls = fields.Boolean(
        string='Journaliser les contrôles',
        config_parameter='adi_treasury_transfer_control.log_controls',
        default=True,
        help="Enregistrer un message dans le chatter pour chaque contrôle"
    )
