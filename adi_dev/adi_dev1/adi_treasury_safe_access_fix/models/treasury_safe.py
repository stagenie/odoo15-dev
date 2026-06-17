# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError

ADMIN_GROUP = 'adi_treasury_safe_access_fix.group_treasury_safe_admin'


class TreasurySafe(models.Model):
    _inherit = 'treasury.safe'

    # Indicateur (non stocké) : l'utilisateur courant peut-il gérer les
    # responsables ? Utilisé pour rendre le champ responsible_ids readonly
    # en interface pour tout le monde sauf le groupe « Admin coffres ».
    can_manage_responsibles = fields.Boolean(
        string="Peut gérer les responsables",
        compute='_compute_can_manage_responsibles',
    )

    @api.depends_context('uid')
    def _compute_can_manage_responsibles(self):
        allowed = self.env.su or self.env.user.has_group(ADMIN_GROUP)
        for rec in self:
            rec.can_manage_responsibles = allowed

    def _check_responsibles_manager(self):
        if self.env.su or self.env.user.has_group(ADMIN_GROUP):
            return
        raise AccessError(_(
            "Accès refusé : seuls les membres du groupe "
            "« Trésorerie / Admin coffres » peuvent définir ou modifier "
            "la liste des Responsables d'un coffre (qui détermine qui peut "
            "consulter le coffre)."
        ))

    def write(self, vals):
        # Verrou ORM : empêche toute modification de responsible_ids hors
        # groupe Admin coffres (contourne le readonly UI via RPC).
        if 'responsible_ids' in vals:
            self._check_responsibles_manager()
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        # À la création, seul un Admin coffres peut fixer des responsables.
        if any(v.get('responsible_ids') for v in vals_list):
            self._check_responsibles_manager()
        return super().create(vals_list)
