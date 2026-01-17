# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _check_team_access(self):
        """
        Vérifie si l'utilisateur a le droit de valider ce BL.

        Règles :
        - Si l'utilisateur a le groupe "Peut valider les BL de tous les dépôts" → OK
        - Sinon, vérifier que l'équipe commerciale de l'entrepôt du BL correspond à l'équipe de l'utilisateur

        Returns:
            bool: True si l'utilisateur peut valider, False sinon
        """
        self.ensure_one()

        # Si l'utilisateur a le groupe spécial, il peut tout valider
        if self.env.user.has_group('adi_picking_team_control.group_validate_all_pickings'):
            return True

        # Récupérer l'équipe commerciale via l'entrepôt du BL
        warehouse = self.picking_type_id.warehouse_id
        if not warehouse:
            # Pas d'entrepôt lié (cas rare), on autorise
            return True

        warehouse_team = warehouse.team_id
        if not warehouse_team:
            # Pas d'équipe sur l'entrepôt, on autorise
            return True

        # Récupérer les équipes de l'utilisateur
        user_teams = self.env.user.sale_team_id
        if not user_teams:
            # L'utilisateur n'a pas d'équipe configurée
            # On vérifie s'il est membre d'une équipe via crm_team_member
            team_members = self.env['crm.team.member'].search([
                ('user_id', '=', self.env.user.id)
            ])
            user_teams = team_members.mapped('crm_team_id')

        # Vérifier si l'équipe de l'entrepôt est dans les équipes de l'utilisateur
        if warehouse_team in user_teams:
            return True

        return False

    def _check_warehouse_access(self, location_dest_id):
        """
        Vérifie si l'utilisateur peut utiliser l'entrepôt de destination.

        Args:
            location_dest_id: ID de la location de destination

        Returns:
            bool: True si l'utilisateur peut utiliser cet entrepôt, False sinon
        """
        # Si l'utilisateur a le groupe spécial, il peut tout modifier
        if self.env.user.has_group('adi_picking_team_control.group_validate_all_pickings'):
            return True

        # Vérifier si l'utilisateur a des restrictions d'entrepôts configurées
        available_warehouse_ids = self.env.user.available_warehouse_ids
        if not available_warehouse_ids:
            # Pas de restrictions configurées, on autorise
            return True

        # Récupérer l'entrepôt de la location de destination (en sudo pour éviter les erreurs d'accès)
        location = self.env['stock.location'].sudo().browse(location_dest_id)
        warehouse = location.warehouse_id

        if not warehouse:
            # Pas d'entrepôt trouvé, on autorise (cas des locations non liées à un entrepôt)
            return True

        # Vérifier si l'entrepôt est dans la liste des entrepôts autorisés
        if warehouse.id in available_warehouse_ids.ids:
            return True

        return False

    def button_validate(self):
        """
        Surcharge de la méthode de validation pour ajouter le contrôle d'équipe.
        """
        for picking in self:
            # Contrôle d'accès par équipe commerciale
            if not picking._check_team_access():
                # Récupérer l'équipe de l'entrepôt du BL
                warehouse = picking.picking_type_id.warehouse_id
                warehouse_team_name = warehouse.team_id.name if warehouse and warehouse.team_id else 'N/A'
                warehouse_name = warehouse.name if warehouse else 'N/A'

                # Récupérer les équipes de l'utilisateur
                user_teams = self.env.user.sale_team_id or self.env['crm.team.member'].search([
                    ('user_id', '=', self.env.user.id)
                ]).mapped('crm_team_id')
                user_team_names = ', '.join(user_teams.mapped('name')) if user_teams else 'Aucune'

                _logger.warning(
                    f"Tentative de validation non autorisée du BL {picking.name} par {self.env.user.name}. "
                    f"Entrepôt: {warehouse_name}, Équipe de l'entrepôt: {warehouse_team_name}, "
                    f"Équipe(s) de l'utilisateur: {user_team_names}"
                )

                raise AccessError(_(
                    "Vous ne pouvez pas valider ce bon de livraison.\n\n"
                    "Raison : Ce BL provient de l'entrepôt '%s' qui appartient à l'équipe commerciale '%s', "
                    "mais vous appartenez à l'équipe '%s'.\n\n"
                    "Seuls les membres de l'équipe '%s' ou les utilisateurs avec "
                    "le groupe 'Peut valider les BL de tous les dépôts' peuvent valider ce BL."
                ) % (warehouse_name, warehouse_team_name, user_team_names, warehouse_team_name))

        return super(StockPicking, self).button_validate()

    def write(self, vals):
        """
        Surcharge de la méthode write pour contrôler la modification de l'entrepôt.
        """
        # Contrôle de la modification de l'entrepôt de livraison
        if 'location_dest_id' in vals:
            for picking in self:
                if not picking._check_warehouse_access(vals['location_dest_id']):
                    # Utiliser sudo pour lire les informations nécessaires au message d'erreur
                    location = self.env['stock.location'].sudo().browse(vals['location_dest_id'])
                    warehouse = location.warehouse_id
                    warehouse_name = warehouse.name if warehouse else location.name

                    authorized_warehouses = self.env.user.available_warehouse_ids
                    authorized_names = ', '.join(authorized_warehouses.mapped('name')) if authorized_warehouses else 'Aucun'

                    _logger.warning(
                        f"Tentative de modification non autorisée de l'entrepôt du BL {picking.name} "
                        f"par {self.env.user.name}. Nouvel entrepôt: {warehouse_name}"
                    )

                    raise AccessError(_(
                        "Vous ne pouvez pas modifier l'entrepôt de livraison vers '%s'.\n\n"
                        "Raison : Cet entrepôt n'est pas dans votre liste d'entrepôts autorisés.\n\n"
                        "Vos entrepôts autorisés : %s\n\n"
                        "Contactez votre administrateur ou un utilisateur avec le groupe "
                        "'Peut valider les BL de tous les dépôts' pour effectuer cette modification."
                    ) % (warehouse_name, authorized_names))

        return super(StockPicking, self).write(vals)
