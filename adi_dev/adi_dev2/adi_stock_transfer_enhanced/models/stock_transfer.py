# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockTransfer(models.Model):
    """
    Extension du modèle adi.stock.transfer pour la réservation multi-source.

    Principales modifications:
    - Ajout du champ use_multi_source pour activer/désactiver le comportement
    - Surcharge de _create_single_picking pour appeler action_assign()
    - Surcharge de _create_inter_company_pickings pour appeler action_assign()
    - Enregistrement de la répartition des sources après réservation
    """
    _inherit = 'adi.stock.transfer'

    # === Nouveaux Champs ===
    use_multi_source = fields.Boolean(
        'Réservation Multi-Source',
        default=True,
        help="Si activé, le système réserve automatiquement dans les sous-emplacements "
             "de l'emplacement source sélectionné. Désactivez pour le comportement legacy "
             "(emplacement strict uniquement)."
    )

    # === Champs Équipe (si pas déjà définis dans le parent) ===
    source_team_id = fields.Many2one(
        'crm.team',
        string='Équipe Source',
        help="Équipe commerciale responsable de l'envoi"
    )
    dest_team_id = fields.Many2one(
        'crm.team',
        string='Équipe Destination',
        help="Équipe commerciale responsable de la réception"
    )

    # === Accès aux sources pour l'onglet ===
    source_allocation_ids = fields.One2many(
        'adi.stock.transfer.line.source',
        'transfer_id',
        string='Répartition des Sources',
        readonly=True
    )
    source_allocation_count = fields.Integer(
        compute='_compute_source_allocation_count',
        string='Nb Allocations'
    )

    @api.depends('source_allocation_ids')
    def _compute_source_allocation_count(self):
        for record in self:
            record.source_allocation_count = len(record.source_allocation_ids)

    source_location_order = fields.Selection([
        ('complete_name', 'Ordre Alphabétique'),
        ('id', 'Ordre de Création'),
    ], string='Priorité Emplacements',
        default='complete_name',
        help="Définit l'ordre de priorité pour la réservation multi-source"
    )

    # === Champs informatifs ===
    has_child_locations = fields.Boolean(
        compute='_compute_has_child_locations',
        string='Sous-emplacements disponibles'
    )
    child_locations_info = fields.Char(
        compute='_compute_has_child_locations',
        string='Info sous-emplacements'
    )

    @api.depends('source_location_id')
    def _compute_has_child_locations(self):
        """Vérifie si l'emplacement source a des sous-emplacements"""
        for record in self:
            if record.source_location_id:
                child_count = self.env['stock.location'].search_count([
                    ('id', 'child_of', record.source_location_id.id),
                    ('id', '!=', record.source_location_id.id),
                    ('usage', '=', 'internal')
                ])
                record.has_child_locations = child_count > 0
                if child_count > 0:
                    record.child_locations_info = _("%d sous-emplacement(s) disponible(s)") % child_count
                else:
                    record.child_locations_info = _("Aucun sous-emplacement")
            else:
                record.has_child_locations = False
                record.child_locations_info = False

    @api.onchange('source_warehouse_id')
    def _onchange_source_warehouse_enhanced(self):
        """Proposer automatiquement l'emplacement racine du stock"""
        if self.source_warehouse_id and self.use_multi_source:
            # Proposer l'emplacement racine (lot_stock_id) par défaut
            self.source_location_id = self.source_warehouse_id.lot_stock_id

    def _create_single_picking(self):
        """
        Surcharge pour ajouter la réservation automatique multi-source.

        Après création du picking, appelle action_assign() pour que Odoo
        réserve automatiquement dans les sous-emplacements disponibles.
        """
        # Appeler la méthode parente
        super(StockTransfer, self)._create_single_picking()

        # En mode multi-source, déclencher la réservation automatique
        if self.use_multi_source and self.source_picking_id:
            self._apply_multi_source_reservation(self.source_picking_id)

    def _create_inter_company_pickings(self):
        """
        Surcharge pour ajouter la réservation automatique multi-source
        aux transferts inter-sociétés.
        """
        # Appeler la méthode parente
        super(StockTransfer, self)._create_inter_company_pickings()

        # En mode multi-source, déclencher la réservation automatique
        if self.use_multi_source and self.source_picking_id:
            self._apply_multi_source_reservation(self.source_picking_id)

    def _apply_multi_source_reservation(self, picking):
        """
        Applique la réservation multi-source sur un picking.

        1. Appelle action_assign() pour réserver automatiquement
        2. Vérifie que la réservation est complète
        3. Enregistre la répartition des sources pour traçabilité
        """
        self.ensure_one()

        if not picking:
            return

        # Exécuter la réservation automatique
        picking.action_assign()

        # Vérifier que la réservation est complète
        if picking.state != 'assigned':
            # Calculer ce qui manque
            missing_products = []
            for move in picking.move_lines:
                if move.state != 'assigned':
                    reserved = sum(move.move_line_ids.mapped('product_uom_qty'))
                    missing = move.product_uom_qty - reserved
                    if missing > 0:
                        missing_products.append(
                            f"• {move.product_id.display_name}: manque {missing} {move.product_uom.name}"
                        )

            if missing_products:
                # Annuler la réservation partielle et le picking
                picking.action_cancel()
                raise ValidationError(_(
                    "La réservation multi-source n'a pas pu être complétée!\n\n"
                    "Produits avec quantité insuffisante:\n%s\n\n"
                    "Veuillez vérifier la disponibilité du stock dans tous les emplacements."
                ) % '\n'.join(missing_products))

        # Enregistrer la répartition des sources pour traçabilité
        self._record_source_allocation(picking)

        self.message_post(
            body=_("Réservation multi-source effectuée automatiquement. "
                   "Voir le détail dans les lignes de transfert.")
        )

    def _record_source_allocation(self, picking):
        """
        Enregistre la répartition des sources pour chaque ligne de transfert.

        Crée des enregistrements adi.stock.transfer.line.source basés sur
        les stock.move.line créés par action_assign().
        """
        self.ensure_one()

        SourceLine = self.env['adi.stock.transfer.line.source']

        for move in picking.move_lines:
            # Trouver la ligne de transfert correspondante
            transfer_line = self.transfer_line_ids.filtered(
                lambda l: l.product_id.id == move.product_id.id
            )

            if not transfer_line:
                continue

            transfer_line = transfer_line[0]

            # Supprimer les anciennes sources (en cas de re-réservation)
            transfer_line.source_line_ids.unlink()

            # Créer les nouvelles sources basées sur les move_line_ids
            for move_line in move.move_line_ids:
                if move_line.product_uom_qty > 0:
                    SourceLine.create({
                        'line_id': transfer_line.id,
                        'location_id': move_line.location_id.id,
                        'quantity_reserved': move_line.product_uom_qty,
                        'quantity_done': 0.0,
                        'move_line_id': move_line.id,
                    })

    def _update_source_quantities_done(self):
        """Met à jour les quantités traitées dans les enregistrements source"""
        self.ensure_one()

        for line in self.transfer_line_ids:
            for source in line.source_line_ids:
                if source.move_line_id:
                    source.quantity_done = source.move_line_id.qty_done
                else:
                    # Si pas de lien direct, utiliser la quantité réservée
                    source.quantity_done = source.quantity_reserved

    def action_view_source_allocation(self):
        """Action pour voir la répartition des sources de tout le transfert"""
        self.ensure_one()
        return {
            'name': _('Répartition des Sources - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'adi.stock.transfer.line.source',
            'view_mode': 'tree',
            'domain': [('transfer_id', '=', self.id)],
            'context': {
                'create': False,
                'edit': False,
                'group_by': ['line_id'],
            },
        }

    # =========================================================================
    # RESTRICTION PAR ÉQUIPE
    # =========================================================================

    def _is_team_restriction_enabled(self):
        """Vérifie si la restriction par équipe est activée dans la configuration"""
        return self.env['ir.config_parameter'].sudo().get_param(
            'adi_stock_transfer_enhanced.restrict_by_team', 'False'
        ).lower() == 'true'

    def _get_team_members(self, team):
        """Retourne les utilisateurs membres d'une équipe"""
        if not team:
            return self.env['res.users']
        return team.member_ids.mapped('user_id')

    def _check_user_in_team(self, team, action_name):
        """
        Vérifie si l'utilisateur courant est membre de l'équipe.
        Lève une erreur si la restriction est activée et l'utilisateur n'est pas autorisé.
        """
        if not self._is_team_restriction_enabled():
            return True

        if not team:
            return True  # Pas d'équipe définie, pas de restriction

        # Les managers peuvent toujours effectuer l'action
        if self.user_has_groups('adi_stock_transfer.group_stock_transfer_manager'):
            return True

        # Vérifier si l'utilisateur est membre de l'équipe
        team_members = self._get_team_members(team)
        if self.env.user not in team_members:
            raise UserError(_(
                "Vous n'êtes pas autorisé à effectuer cette action.\n\n"
                "Action: %(action)s\n"
                "Équipe requise: %(team)s\n\n"
                "Seuls les membres de cette équipe ou les Managers de Transfert peuvent effectuer cette opération."
            ) % {
                'action': action_name,
                'team': team.name,
            })

        return True

    @api.onchange('source_warehouse_id')
    def _onchange_source_warehouse_team(self):
        """Lier automatiquement l'équipe source à l'entrepôt source"""
        if self.source_warehouse_id and self.source_warehouse_id.team_id:
            self.source_team_id = self.source_warehouse_id.team_id

    @api.onchange('dest_warehouse_id')
    def _onchange_dest_warehouse_team(self):
        """Lier automatiquement l'équipe destination à l'entrepôt destination"""
        if self.dest_warehouse_id and self.dest_warehouse_id.team_id:
            self.dest_team_id = self.dest_warehouse_id.team_id

    def action_start_transit(self):
        """
        Surcharge pour ajouter la vérification d'équipe avant l'envoi.
        """
        self.ensure_one()

        # Vérifier si l'utilisateur est membre de l'équipe source
        self._check_user_in_team(self.source_team_id, _("Envoyer le transfert"))

        # En mode multi-source, on doit travailler avec les move_lines
        if self.use_multi_source:
            # Mettre à jour les quantités envoyées sur les lignes de transfert
            for line in self.transfer_line_ids:
                if line.qty_sent == 0:
                    line.qty_sent = line.quantity

            # Valider le picking de sortie en travaillant avec les move_lines
            if self.source_picking_id and self.source_picking_id.state not in ('done', 'cancel'):
                for move in self.source_picking_id.move_lines:
                    transfer_line = self.transfer_line_ids.filtered(
                        lambda l: l.product_id.id == move.product_id.id
                    )
                    if transfer_line:
                        qty_to_send = transfer_line[0].qty_sent
                        # Répartir la quantité sur les move_lines existantes
                        remaining_qty = qty_to_send
                        for move_line in move.move_line_ids:
                            if remaining_qty <= 0:
                                break
                            qty_for_line = min(move_line.product_uom_qty, remaining_qty)
                            move_line.qty_done = qty_for_line
                            remaining_qty -= qty_for_line

                self.source_picking_id.with_context(skip_backorder=True).button_validate()

            # Mettre à jour les quantity_done dans les sources
            self._update_source_quantities_done()

            self.state = 'in_transit'
            self.message_post(body=_("Produits envoyés - En transit"))
        else:
            # Mode legacy: appeler la méthode parente originale (sans notre surcharge)
            # On doit reproduire le comportement du module parent
            for line in self.transfer_line_ids:
                if line.qty_sent == 0:
                    line.qty_sent = line.quantity

            if self.source_picking_id and self.source_picking_id.state not in ('done', 'cancel'):
                for move in self.source_picking_id.move_lines:
                    transfer_line = self.transfer_line_ids.filtered(
                        lambda l: l.product_id.id == move.product_id.id
                    )
                    if transfer_line:
                        move.quantity_done = transfer_line[0].qty_sent
                # IMPORTANT: skip_backorder=True pour éviter le wizard de backorder
                # qui bloque la validation si les quantités sont partielles
                self.source_picking_id.with_context(skip_backorder=True).button_validate()

            self.state = 'in_transit'
            self.message_post(body=_("Produits envoyés - En transit"))

    def action_done(self):
        """
        Surcharge pour ajouter la vérification d'équipe avant la réception.
        """
        self.ensure_one()

        # Vérifier si l'utilisateur est membre de l'équipe destination
        self._check_user_in_team(self.dest_team_id, _("Confirmer la réception"))

        # Appeler la méthode parente (ouvre le wizard de confirmation)
        return super(StockTransfer, self).action_done()
