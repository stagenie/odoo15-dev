# -*- coding: utf-8 -*-
from odoo import fields, models, api


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    # Override du style de template pour cette équipe
    report_template_style = fields.Selection([
        ('default', 'Utiliser la configuration globale'),
        ('light', 'Light - Style épuré'),
        ('box', 'Box - Encadré'),
        ('bold', 'Bold - Prononcé'),
    ], string='Style de template',
       default='default',
       help="Style de rapport spécifique à cette équipe. "
            "'Utiliser la configuration globale' applique le style défini dans les paramètres.")

    # Override pour les infos fiscales
    fiscal_info_in_footer = fields.Selection([
        ('default', 'Utiliser la configuration globale'),
        ('yes', 'Oui - En pied de page'),
        ('no', 'Non - En en-tête'),
    ], string='Infos fiscales en pied de page',
       default='default',
       help="Position des informations fiscales pour cette équipe.")

    def get_report_template_style(self):
        """Retourne le style effectif à utiliser pour cette équipe"""
        self.ensure_one()
        if self.report_template_style and self.report_template_style != 'default':
            return self.report_template_style
        return self.company_id.report_template_style or 'light'

    def get_fiscal_info_in_footer(self):
        """Retourne si les infos fiscales doivent être en footer pour cette équipe"""
        self.ensure_one()
        if self.fiscal_info_in_footer and self.fiscal_info_in_footer != 'default':
            return self.fiscal_info_in_footer == 'yes'
        return self.company_id.fiscal_info_in_footer
