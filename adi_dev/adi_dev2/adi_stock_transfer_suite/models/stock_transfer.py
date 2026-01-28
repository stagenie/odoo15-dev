# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockTransfer(models.Model):
    """
    Extension du modèle adi.stock.transfer pour la gestion des envois partiels.

    Fonctionnalités ajoutées:
    - Pré-remplissage de qty_sent à l'approbation
    - Calcul des quantités non envoyées
    - Création de transferts de renvoi pour le reste
    - Traçabilité origine ↔ renvoi
    """
    _inherit = 'adi.stock.transfer'

    # === Champs de traçabilité ===
    origin_transfer_id = fields.Many2one(
        'adi.stock.transfer',
        string='Transfert Origine',
        readonly=True,
        copy=False,
        help="Référence au transfert original dont celui-ci est le renvoi"
    )

    resend_transfer_id = fields.Many2one(
        'adi.stock.transfer',
        string='Transfert de Renvoi',
        readonly=True,
        copy=False,
        help="Référence au transfert créé pour renvoyer le reste"
    )

    resend_transfer_ids = fields.One2many(
        'adi.stock.transfer',
        'origin_transfer_id',
        string='Transferts de Renvoi',
        readonly=True,
        help="Tous les transferts de renvoi créés depuis ce transfert"
    )

    resend_count = fields.Integer(
        compute='_compute_resend_count',
        string='Nombre de Renvois'
    )

    is_resend = fields.Boolean(
        string='Est un Renvoi',
        readonly=True,
        copy=False,
        default=False,
        help="Indique si ce transfert a été créé pour renvoyer des quantités non envoyées"
    )

    is_closed_without_resend = fields.Boolean(
        string='Clôturé sans Renvoi',
        readonly=True,
        copy=False,
        default=False,
        help="Indique que le transfert a été volontairement clôturé sans renvoyer le reste"
    )

    # === Champs calculés pour la gestion des envois partiels ===
    qty_not_sent_total = fields.Float(
        compute='_compute_qty_not_sent_total',
        string='Total Non Envoyé',
        digits='Product Unit of Measure',
        store=True,
        help="Total des quantités demandées mais non envoyées"
    )

    has_pending_resend = fields.Boolean(
        compute='_compute_has_pending_resend',
        string='Renvoi en Attente',
        store=True,
        help="Indique si des quantités n'ont pas été envoyées et peuvent faire l'objet d'un renvoi"
    )

    can_create_resend = fields.Boolean(
        compute='_compute_can_create_resend',
        string='Peut Créer Renvoi',
        help="Indique si le bouton 'Créer demande de renvoi' doit être visible"
    )

    can_close_without_resend = fields.Boolean(
        compute='_compute_can_close_without_resend',
        string='Peut Clôturer',
        help="Indique si le bouton 'Clôturer sans renvoi' doit être visible"
    )

    # === Champ pour afficher l'origine dans le nom ===
    display_name_with_origin = fields.Char(
        compute='_compute_display_name_with_origin',
        string='Nom avec Origine'
    )

    @api.depends('resend_transfer_ids')
    def _compute_resend_count(self):
        """Calcule le nombre de transferts de renvoi"""
        for record in self:
            record.resend_count = len(record.resend_transfer_ids)

    @api.depends('transfer_line_ids.qty_not_sent')
    def _compute_qty_not_sent_total(self):
        """Calcule le total des quantités non envoyées"""
        for record in self:
            record.qty_not_sent_total = sum(
                record.transfer_line_ids.mapped('qty_not_sent')
            )

    @api.depends('state', 'qty_not_sent_total')
    def _compute_has_pending_resend(self):
        """Vérifie si des quantités peuvent faire l'objet d'un renvoi"""
        for record in self:
            record.has_pending_resend = (
                record.state == 'done' and
                record.qty_not_sent_total > 0
            )

    @api.depends('state', 'has_pending_resend', 'resend_transfer_id', 'is_closed_without_resend')
    def _compute_can_create_resend(self):
        """Détermine si le bouton de création de renvoi doit être visible"""
        for record in self:
            record.can_create_resend = (
                record.state == 'done' and
                record.has_pending_resend and
                not record.resend_transfer_id and
                not record.is_closed_without_resend
            )

    @api.depends('state', 'has_pending_resend', 'resend_transfer_id', 'is_closed_without_resend')
    def _compute_can_close_without_resend(self):
        """Détermine si le bouton de clôture sans renvoi doit être visible"""
        for record in self:
            record.can_close_without_resend = (
                record.state == 'done' and
                record.has_pending_resend and
                not record.resend_transfer_id and
                not record.is_closed_without_resend
            )

    @api.depends('name', 'origin_transfer_id', 'is_resend')
    def _compute_display_name_with_origin(self):
        """Affiche le nom avec l'origine si c'est un renvoi"""
        for record in self:
            if record.is_resend and record.origin_transfer_id:
                record.display_name_with_origin = _(
                    "%(name)s (Renvoi de %(origin)s)"
                ) % {
                    'name': record.name or _('Nouveau'),
                    'origin': record.origin_transfer_id.name,
                }
            else:
                record.display_name_with_origin = record.name or _('Nouveau')

    # =========================================================================
    # SURCHARGE: Approbation - Pré-remplir qty_sent
    # =========================================================================

    def action_approve(self):
        """
        Surcharge pour pré-remplir qty_sent = quantity à l'approbation.
        Cela permet à l'expéditeur de voir et modifier la quantité à envoyer.
        """
        # Appeler la méthode parente (crée les pickings, etc.)
        result = super(StockTransfer, self).action_approve()

        # Pré-remplir qty_sent avec la quantité demandée pour chaque ligne
        for transfer in self:
            for line in transfer.transfer_line_ids:
                if line.qty_sent == 0:
                    line.qty_sent = line.quantity

            transfer.message_post(body=_(
                "Quantités à envoyer pré-remplies. "
                "Vous pouvez modifier les quantités avant l'envoi si nécessaire."
            ))

        return result

    # =========================================================================
    # SURCHARGE: Envoi - Ajuster les moves pour éviter les backorders
    # =========================================================================

    def action_start_transit(self):
        """
        Surcharge complète pour gérer les envois partiels sans créer de backorders.

        Problème résolu:
        - À l'approbation, les moves sont créés avec product_uom_qty = quantity
        - Si on envoie moins (qty_sent < quantity), Odoo crée des backorders
        - Solution: Ajuster product_uom_qty = qty_sent AVANT la validation

        Cela garantit que quantity_done == product_uom_qty, donc pas de backorder.
        """
        self.ensure_one()

        # Vérification équipe (si le module enhanced est présent)
        if hasattr(self, '_check_user_in_team') and hasattr(self, 'source_team_id'):
            self._check_user_in_team(self.source_team_id, _("Envoyer le transfert"))

        # Vérifier qu'il y a au moins une quantité à envoyer
        total_to_send = sum(self.transfer_line_ids.mapped('qty_sent'))
        if total_to_send <= 0:
            raise UserError(_(
                "Vous devez spécifier au moins une quantité à envoyer.\n"
                "Toutes les quantités envoyées sont à 0."
            ))

        # Message informatif si envoi partiel
        lines_with_partial = self.transfer_line_ids.filtered(
            lambda l: l.qty_sent < l.quantity and l.qty_sent > 0
        )
        if lines_with_partial:
            partial_info = []
            for line in lines_with_partial:
                partial_info.append(
                    f"• {line.product_id.display_name}: "
                    f"{line.qty_sent}/{line.quantity} {line.product_uom_id.name}"
                )
            self.message_post(body=_(
                "<strong>Envoi partiel détecté:</strong><br/>"
                "%(details)s<br/><br/>"
                "Les quantités non envoyées pourront faire l'objet d'un renvoi "
                "après la réception."
            ) % {'details': '<br/>'.join(partial_info)})

        # =====================================================================
        # AJUSTER LES MOVES SOURCE AVANT VALIDATION
        # =====================================================================
        if self.source_picking_id and self.source_picking_id.state not in ('done', 'cancel'):
            # D'abord, libérer toutes les réservations pour pouvoir modifier les quantités
            self.source_picking_id.do_unreserve()

            for move in self.source_picking_id.move_lines:
                transfer_line = self.transfer_line_ids.filtered(
                    lambda l: l.product_id.id == move.product_id.id
                )
                if transfer_line:
                    qty_to_send = transfer_line[0].qty_sent

                    # CLEF: Ajuster product_uom_qty pour correspondre à qty_sent
                    # Cela évite la création de backorders
                    move.product_uom_qty = qty_to_send

            # Re-réserver avec les nouvelles quantités
            self.source_picking_id.action_assign()

            # Maintenant définir les qty_done
            for move in self.source_picking_id.move_lines:
                transfer_line = self.transfer_line_ids.filtered(
                    lambda l: l.product_id.id == move.product_id.id
                )
                if transfer_line:
                    qty_to_send = transfer_line[0].qty_sent
                    move.quantity_done = qty_to_send

                    # Définir qty_done sur les move_lines
                    for move_line in move.move_line_ids:
                        move_line.qty_done = move_line.product_uom_qty

            # Valider le picking source - SANS création de backorder
            self.source_picking_id.with_context(skip_backorder=True).button_validate()

        # Mettre à jour les sources si la méthode existe
        if hasattr(self, '_update_source_quantities_done'):
            self._update_source_quantities_done()

        # =====================================================================
        # AJUSTER LES MOVES DESTINATION
        # =====================================================================
        # Le picking destination doit aussi avoir ses moves ajustés
        # pour correspondre aux quantités réellement envoyées
        if self.dest_picking_id and self.dest_picking_id.state not in ('done', 'cancel'):
            for move in self.dest_picking_id.move_lines:
                transfer_line = self.transfer_line_ids.filtered(
                    lambda l: l.product_id.id == move.product_id.id
                )
                if transfer_line:
                    qty_sent = transfer_line[0].qty_sent

                    # Ajuster product_uom_qty du move destination aussi
                    # Car à la réception, on ne recevra que qty_sent
                    if qty_sent < move.product_uom_qty:
                        move.product_uom_qty = qty_sent

        self.state = 'in_transit'
        self.message_post(body=_("Produits envoyés - En transit"))

    def action_done_confirmed(self):
        """
        Surcharge pour ajuster les moves destination avant validation.

        Garantit que product_uom_qty == qty_received pour éviter les backorders.
        """
        self.ensure_one()

        # Vérification équipe (si le module enhanced est présent)
        if hasattr(self, '_check_user_in_team') and hasattr(self, 'dest_team_id'):
            self._check_user_in_team(self.dest_team_id, _("Confirmer la réception"))

        # Forcer qty_received = qty_sent pour chaque ligne
        for line in self.transfer_line_ids:
            if line.qty_sent == 0:
                line.qty_sent = line.quantity
            line.qty_received = line.qty_sent

        # =====================================================================
        # AJUSTER LES MOVES DESTINATION AVANT VALIDATION
        # =====================================================================
        if self.dest_picking_id and self.dest_picking_id.state not in ('done', 'cancel'):
            # D'abord, libérer toutes les réservations
            self.dest_picking_id.do_unreserve()

            for move in self.dest_picking_id.move_lines:
                transfer_line = self.transfer_line_ids.filtered(
                    lambda l: l.product_id.id == move.product_id.id
                )
                if transfer_line:
                    qty_received = transfer_line[0].qty_received

                    # CLEF: Ajuster product_uom_qty pour correspondre à qty_received
                    move.product_uom_qty = qty_received

            # Re-réserver avec les nouvelles quantités
            self.dest_picking_id.action_assign()

            # Maintenant définir les qty_done
            for move in self.dest_picking_id.move_lines:
                transfer_line = self.transfer_line_ids.filtered(
                    lambda l: l.product_id.id == move.product_id.id
                )
                if transfer_line:
                    qty_received = transfer_line[0].qty_received
                    move.quantity_done = qty_received

                    # Définir qty_done sur les move_lines
                    for move_line in move.move_line_ids:
                        move_line.qty_done = move_line.product_uom_qty

            # Valider le picking destination - SANS création de backorder
            self.dest_picking_id.with_context(skip_backorder=True).button_validate()

        self.state = 'done'

        # Message adapté
        if self.qty_not_sent_total > 0:
            self.message_post(body=_(
                "Réception complète - Transfert terminé.<br/>"
                "<strong>Note:</strong> %(qty)s unités n'ont pas été envoyées. "
                "Vous pouvez créer une demande de renvoi ou clôturer sans renvoi."
            ) % {'qty': self.qty_not_sent_total})
        else:
            self.message_post(body=_("Réception complète - Transfert terminé"))

    # =========================================================================
    # NOUVELLES ACTIONS: Gestion des renvois
    # =========================================================================

    def action_create_resend(self):
        """
        Crée un nouveau transfert pour renvoyer les quantités non envoyées.

        Le nouveau transfert:
        - A les mêmes entrepôts source/destination
        - Contient uniquement les produits avec qty_not_sent > 0
        - Est marqué comme 'is_resend' avec référence à l'origine
        """
        self.ensure_one()

        if not self.can_create_resend:
            raise UserError(_(
                "Impossible de créer un transfert de renvoi.\n"
                "Vérifiez que le transfert est terminé et qu'il y a des quantités non envoyées."
            ))

        # Filtrer les lignes avec des quantités non envoyées
        lines_to_resend = self.transfer_line_ids.filtered(
            lambda l: l.qty_not_sent > 0
        )

        if not lines_to_resend:
            raise UserError(_("Aucune quantité à renvoyer."))

        # Préparer les valeurs du nouveau transfert
        resend_vals = {
            'source_company_id': self.source_company_id.id,
            'dest_company_id': self.dest_company_id.id,
            'source_warehouse_id': self.source_warehouse_id.id,
            'dest_warehouse_id': self.dest_warehouse_id.id,
            'source_location_id': self.source_location_id.id,
            'dest_location_id': self.dest_location_id.id,
            'requester_id': self.env.user.id,
            'origin_transfer_id': self.id,
            'is_resend': True,
            'note': _(
                "Renvoi des quantités non envoyées du transfert %(origin)s"
            ) % {'origin': self.name},
            'transfer_line_ids': [],
        }

        # Copier les paramètres enhanced si présents
        if hasattr(self, 'use_multi_source'):
            resend_vals['use_multi_source'] = self.use_multi_source
        if hasattr(self, 'source_location_order'):
            resend_vals['source_location_order'] = self.source_location_order
        if hasattr(self, 'source_team_id') and self.source_team_id:
            resend_vals['source_team_id'] = self.source_team_id.id
        if hasattr(self, 'dest_team_id') and self.dest_team_id:
            resend_vals['dest_team_id'] = self.dest_team_id.id

        # Préparer les lignes
        for line in lines_to_resend:
            resend_vals['transfer_line_ids'].append((0, 0, {
                'product_id': line.product_id.id,
                'product_uom_id': line.product_uom_id.id,
                'quantity': line.qty_not_sent,
                'note': _(
                    "Renvoi de %(qty)s (non envoyé sur %(origin_qty)s demandé)"
                ) % {
                    'qty': line.qty_not_sent,
                    'origin_qty': line.quantity,
                },
            }))

        # Créer le nouveau transfert
        resend_transfer = self.create(resend_vals)

        # Mettre à jour le transfert original
        self.write({
            'resend_transfer_id': resend_transfer.id,
        })

        # Message de confirmation
        self.message_post(body=_(
            "Transfert de renvoi <a href='#' data-oe-model='adi.stock.transfer' "
            "data-oe-id='%(id)s'>%(name)s</a> créé avec succès."
        ) % {
            'id': resend_transfer.id,
            'name': resend_transfer.name or _('Nouveau'),
        })

        resend_transfer.message_post(body=_(
            "Ce transfert a été créé pour renvoyer les quantités non envoyées "
            "du transfert <a href='#' data-oe-model='adi.stock.transfer' "
            "data-oe-id='%(id)s'>%(name)s</a>."
        ) % {
            'id': self.id,
            'name': self.name,
        })

        # Ouvrir le nouveau transfert
        return {
            'type': 'ir.actions.act_window',
            'name': _('Transfert de Renvoi'),
            'res_model': 'adi.stock.transfer',
            'res_id': resend_transfer.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_close_without_resend(self):
        """
        Clôture le transfert sans créer de renvoi pour les quantités non envoyées.
        """
        self.ensure_one()

        if not self.can_close_without_resend:
            raise UserError(_(
                "Impossible de clôturer ce transfert.\n"
                "Vérifiez que le transfert est terminé et qu'il y a des quantités non envoyées."
            ))

        # Demander confirmation
        return {
            'type': 'ir.actions.act_window',
            'name': _('Confirmer la Clôture'),
            'res_model': 'adi.stock.transfer.close.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_transfer_id': self.id,
            },
        }

    def _action_close_without_resend_confirmed(self):
        """Exécute la clôture sans renvoi après confirmation"""
        self.ensure_one()

        # Préparer le résumé des quantités non envoyées
        lines_not_sent = self.transfer_line_ids.filtered(lambda l: l.qty_not_sent > 0)
        summary = []
        for line in lines_not_sent:
            summary.append(
                f"• {line.product_id.display_name}: {line.qty_not_sent} {line.product_uom_id.name}"
            )

        self.write({
            'is_closed_without_resend': True,
        })

        self.message_post(body=_(
            "<strong>Transfert clôturé sans renvoi</strong><br/><br/>"
            "Les quantités suivantes n'ont pas été envoyées et ne feront pas "
            "l'objet d'un renvoi:<br/>%(summary)s"
        ) % {'summary': '<br/>'.join(summary)})

        return True

    # =========================================================================
    # ACTIONS DE NAVIGATION
    # =========================================================================

    def action_view_resend_transfer(self):
        """Ouvre le transfert de renvoi"""
        self.ensure_one()
        if self.resend_transfer_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Transfert de Renvoi'),
                'res_model': 'adi.stock.transfer',
                'res_id': self.resend_transfer_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return False

    def action_view_origin_transfer(self):
        """Ouvre le transfert d'origine"""
        self.ensure_one()
        if self.origin_transfer_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Transfert Origine'),
                'res_model': 'adi.stock.transfer',
                'res_id': self.origin_transfer_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return False

    def action_view_all_resend_transfers(self):
        """Ouvre la liste de tous les transferts de renvoi"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Transferts de Renvoi'),
            'res_model': 'adi.stock.transfer',
            'view_mode': 'tree,form',
            'domain': [('origin_transfer_id', '=', self.id)],
            'target': 'current',
        }


class StockTransferCloseWizard(models.TransientModel):
    """Wizard de confirmation pour clôturer sans renvoi"""
    _name = 'adi.stock.transfer.close.wizard'
    _description = 'Confirmation de Clôture sans Renvoi'

    transfer_id = fields.Many2one(
        'adi.stock.transfer',
        string='Transfert',
        required=True,
        readonly=True
    )

    lines_summary = fields.Html(
        compute='_compute_lines_summary',
        string='Résumé des Quantités Non Envoyées'
    )

    @api.depends('transfer_id')
    def _compute_lines_summary(self):
        """Calcule le résumé des lignes non envoyées"""
        for wizard in self:
            if wizard.transfer_id:
                lines = wizard.transfer_id.transfer_line_ids.filtered(
                    lambda l: l.qty_not_sent > 0
                )
                if lines:
                    summary_html = '<table class="table table-sm table-bordered">'
                    summary_html += '<thead><tr><th>Produit</th><th>Non Envoyé</th></tr></thead>'
                    summary_html += '<tbody>'
                    for line in lines:
                        summary_html += (
                            f'<tr><td>{line.product_id.display_name}</td>'
                            f'<td class="text-danger">{line.qty_not_sent} {line.product_uom_id.name}</td></tr>'
                        )
                    summary_html += '</tbody></table>'
                    wizard.lines_summary = summary_html
                else:
                    wizard.lines_summary = _('<p>Aucune quantité non envoyée.</p>')
            else:
                wizard.lines_summary = False

    def action_confirm(self):
        """Confirme la clôture sans renvoi"""
        self.ensure_one()
        return self.transfer_id._action_close_without_resend_confirmed()
