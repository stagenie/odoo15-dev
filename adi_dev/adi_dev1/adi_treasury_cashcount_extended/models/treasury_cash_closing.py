# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class TreasuryCashClosing(models.Model):
    _inherit = 'treasury.cash.closing'

    # =============================================
    # COMPTAGE FINAL
    # =============================================

    # Indicateur si le comptage final a été effectué via le wizard
    cash_count_done = fields.Boolean(
        string='Comptage final effectué',
        default=False,
        help="Indique si le comptage final a été effectué via le wizard"
    )

    # Champ calculé pour savoir si le forçage du comptage final est actif
    force_cash_count = fields.Boolean(
        string='Forcer le comptage final',
        compute='_compute_force_cash_count',
        help="Indique si le comptage final est obligatoire pour cette clôture"
    )

    # =============================================
    # AFFICHAGE DANS LES RAPPORTS
    # =============================================

    show_count_in_report = fields.Boolean(
        string='Afficher le comptage dans le rapport',
        compute='_compute_show_count_in_report',
        help="Indique si le détail du comptage doit être affiché dans le rapport"
    )

    # =============================================
    # MÉTHODES COMPUTE
    # =============================================

    @api.depends('cash_id.force_cash_count')
    def _compute_force_cash_count(self):
        """Déterminer si le forçage du comptage final est actif"""
        global_force = self.env['ir.config_parameter'].sudo().get_param(
            'adi_treasury_cashcount_extended.force_cash_count', 'False'
        ) == 'True'

        for closing in self:
            closing.force_cash_count = global_force or (
                closing.cash_id and closing.cash_id.force_cash_count
            )

    @api.depends('cash_id.show_count_in_report')
    def _compute_show_count_in_report(self):
        """Déterminer si le comptage doit être affiché dans le rapport"""
        global_hide = self.env['ir.config_parameter'].sudo().get_param(
            'adi_treasury_cashcount_extended.hide_count_in_report', 'False'
        ) == 'True'

        for closing in self:
            # Si masqué globalement, ne pas afficher
            if global_hide:
                closing.show_count_in_report = False
            # Sinon, utiliser le paramètre de la caisse (True par défaut)
            elif closing.cash_id:
                closing.show_count_in_report = closing.cash_id.show_count_in_report
            else:
                closing.show_count_in_report = True

    # =============================================
    # ACTIONS WIZARD
    # =============================================

    def action_open_cash_count_wizard(self):
        """Ouvrir le wizard de comptage final"""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_(
                "Le comptage ne peut être modifié que pour une clôture en brouillon."
            ))

        wizard = self.env['cash.count.wizard'].create({
            'closing_id': self.id,
        })

        return {
            'name': _('Comptage de Caisse'),
            'type': 'ir.actions.act_window',
            'res_model': 'cash.count.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'active_model': 'treasury.cash.closing',
            }
        }

    # =============================================
    # OVERRIDE ACTIONS
    # =============================================

    def action_confirm(self):
        """Override pour vérifier le comptage final obligatoire"""
        for closing in self:
            # Vérifier le comptage final obligatoire
            if closing.force_cash_count:
                if not closing.cash_count_done:
                    raise ValidationError(_(
                        "Le comptage final des billets et pièces est obligatoire.\n\n"
                        "Veuillez cliquer sur le bouton 'Comptage de caisse' à côté du champ "
                        "'Solde réel' pour effectuer le comptage.\n\n"
                        "Note: Même si le solde est à 0, vous devez valider le wizard de comptage."
                    ))

        return super(TreasuryCashClosing, self).action_confirm()
