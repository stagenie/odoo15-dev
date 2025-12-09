# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Style de template pour les rapports
    report_template_style = fields.Selection([
        ('light', 'Light - Style épuré'),
        ('box', 'Box - Encadré'),
        ('bold', 'Bold - Prononcé'),
    ], string='Style de template', default='light',
       help="Style visuel appliqué aux en-têtes des rapports")

    # Option pour afficher les infos fiscales en pied de page
    fiscal_info_in_footer = fields.Boolean(
        string='Infos fiscales en pied de page',
        default=True,
        help="Afficher RC, AI, NIF, NIS en bas de page au lieu de l'en-tête"
    )

    # Séparateur pour les infos fiscales
    fiscal_info_separator = fields.Char(
        string='Séparateur',
        default=' - ',
        help="Caractère(s) séparant les informations fiscales"
    )

    # Activer/désactiver le template personnalisé
    use_custom_report_template = fields.Boolean(
        string='Utiliser template personnalisé',
        default=False,
        help="Activer les templates de rapport personnalisés"
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Champs liés à la société
    report_template_style = fields.Selection(
        related='company_id.report_template_style',
        readonly=False
    )

    fiscal_info_in_footer = fields.Boolean(
        related='company_id.fiscal_info_in_footer',
        readonly=False
    )

    fiscal_info_separator = fields.Char(
        related='company_id.fiscal_info_separator',
        readonly=False
    )

    use_custom_report_template = fields.Boolean(
        related='company_id.use_custom_report_template',
        readonly=False
    )
