# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TreasuryCashClosingEnhanced(models.Model):
    """
    Extension du modèle de clôture pour afficher et gérer les opérations manuelles
    directement depuis le formulaire de clôture.
    """
    _inherit = 'treasury.cash.closing'

    # ===============================
    # CHAMPS COMPUTED - Opérations manuelles de la période
    # ===============================

    # Opérations manuelles en brouillon (à valider avant confirmation)
    pending_manual_operation_ids = fields.One2many(
        'treasury.cash.operation',
        compute='_compute_pending_manual_operations',
        string='Opérations manuelles à traiter'
    )

    pending_manual_operation_count = fields.Integer(
        string='Opérations à traiter',
        compute='_compute_pending_manual_operations'
    )

    # Toutes les opérations manuelles de la caisse (brouillon ou posted, sans clôture)
    all_pending_manual_operation_ids = fields.One2many(
        'treasury.cash.operation',
        compute='_compute_all_pending_manual_operations',
        string='Toutes les opérations manuelles en attente'
    )

    all_pending_manual_operation_count = fields.Integer(
        string='Total opérations en attente',
        compute='_compute_all_pending_manual_operations'
    )

    # ===============================
    # MÉTHODES COMPUTE
    # ===============================

    @api.depends('cash_id', 'period_start', 'period_end', 'state')
    def _compute_pending_manual_operations(self):
        """
        Calculer les opérations manuelles en brouillon de la période de la clôture.
        Ces opérations doivent être validées avant de pouvoir confirmer la clôture.
        """
        for closing in self:
            if not closing.cash_id or not closing.period_start or not closing.period_end:
                closing.pending_manual_operation_ids = False
                closing.pending_manual_operation_count = 0
                continue

            # Rechercher les opérations manuelles en brouillon dans la période
            domain = [
                ('cash_id', '=', closing.cash_id.id),
                ('is_manual', '=', True),
                ('state', '=', 'draft'),
                ('date', '>=', closing.period_start),
                ('date', '<=', closing.period_end),
                # Pas déjà liées à une autre clôture ou à cette clôture
                '|',
                ('closing_id', '=', False),
                ('closing_id', '=', closing.id),
            ]

            operations = self.env['treasury.cash.operation'].search(domain, order='date asc, id asc')
            closing.pending_manual_operation_ids = operations
            closing.pending_manual_operation_count = len(operations)

    @api.depends('cash_id', 'state')
    def _compute_all_pending_manual_operations(self):
        """
        Calculer TOUTES les opérations manuelles de la caisse qui ne sont pas
        encore dans une clôture validée (brouillon ou posted).
        """
        for closing in self:
            if not closing.cash_id:
                closing.all_pending_manual_operation_ids = False
                closing.all_pending_manual_operation_count = 0
                continue

            # Rechercher toutes les opérations manuelles non clôturées
            # On ne peut pas utiliser closing_id.state dans un domaine search
            # Donc on filtre en deux étapes
            operations = self.env['treasury.cash.operation'].search([
                ('cash_id', '=', closing.cash_id.id),
                ('is_manual', '=', True),
                ('state', 'in', ['draft', 'posted']),
            ], order='date asc, id asc')

            # Filtrer les opérations qui ne sont pas dans une clôture validée
            pending_operations = operations.filtered(
                lambda o: not o.closing_id or o.closing_id.state != 'validated'
            )

            closing.all_pending_manual_operation_ids = pending_operations
            closing.all_pending_manual_operation_count = len(pending_operations)

    # ===============================
    # ACTIONS
    # ===============================

    def action_view_pending_manual_operations(self):
        """
        Afficher les opérations manuelles en brouillon de la période.
        Permet de les consulter, valider ou supprimer.
        """
        self.ensure_one()

        return {
            'name': _('Opérations manuelles à traiter - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.cash.operation',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.pending_manual_operation_ids.ids)],
            'context': {
                'default_cash_id': self.cash_id.id,
                'default_closing_id': self.id,
                'default_is_manual': True,
            },
            'help': """
                <p class="o_view_nocontent_smiling_face">
                    Aucune opération manuelle en brouillon
                </p>
                <p>
                    Toutes les opérations manuelles ont été validées.
                    Vous pouvez maintenant confirmer la clôture.
                </p>
            """
        }

    def action_view_all_pending_operations(self):
        """
        Afficher TOUTES les opérations manuelles en attente de la caisse
        (brouillon + posted non clôturées).
        """
        self.ensure_one()

        return {
            'name': _('Toutes les opérations en attente - %s') % self.cash_id.name,
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.cash.operation',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.all_pending_manual_operation_ids.ids)],
            'context': {
                'default_cash_id': self.cash_id.id,
                'default_is_manual': True,
            },
            'help': """
                <p class="o_view_nocontent_smiling_face">
                    Aucune opération manuelle en attente
                </p>
                <p>
                    Toutes les opérations manuelles sont clôturées.
                </p>
            """
        }

    def action_validate_all_pending_operations(self):
        """
        Valider (comptabiliser) toutes les opérations manuelles en brouillon
        de la période de la clôture.
        """
        self.ensure_one()

        if self.state == 'validated':
            raise UserError(_("Impossible de modifier une clôture validée."))

        draft_operations = self.pending_manual_operation_ids.filtered(
            lambda o: o.state == 'draft'
        )

        if not draft_operations:
            raise UserError(_("Aucune opération en brouillon à valider."))

        # Valider les opérations
        validated_count = 0
        errors = []

        for operation in draft_operations:
            try:
                operation.action_post()
                validated_count += 1
            except Exception as e:
                errors.append(f"- {operation.name}: {str(e)}")

        # Message de résultat
        if validated_count > 0:
            self.message_post(
                body=_("✅ %d opération(s) manuelle(s) validée(s) avec succès.") % validated_count
            )

        if errors:
            error_msg = "\n".join(errors)
            raise UserError(_(
                "Certaines opérations n'ont pas pu être validées :\n%s"
            ) % error_msg)

        # Recharger les opérations de la clôture
        if self.state == 'draft':
            self.action_load_operations()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Opérations validées'),
                'message': _('%d opération(s) validée(s) avec succès.') % validated_count,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_add_pending_operations_to_closing(self):
        """
        Ajouter toutes les opérations manuelles posted (non liées à une clôture)
        de la période à cette clôture.
        """
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_("Cette action n'est disponible qu'en brouillon."))

        # Rechercher les opérations manuelles posted non clôturées de la période
        operations = self.env['treasury.cash.operation'].search([
            ('cash_id', '=', self.cash_id.id),
            ('is_manual', '=', True),
            ('state', '=', 'posted'),
            ('closing_id', '=', False),
            ('date', '>=', self.period_start),
            ('date', '<=', self.period_end),
        ])

        if not operations:
            raise UserError(_("Aucune opération manuelle à ajouter."))

        # Ajouter à la clôture
        operations.write({'closing_id': self.id})

        # Recalculer
        self._compute_totals()
        self._compute_closing_lines()

        self.message_post(
            body=_("✅ %d opération(s) manuelle(s) ajoutée(s) à la clôture.") % len(operations)
        )

        return True

    def action_open_manual_operation_wizard(self):
        """
        Ouvrir un wizard pour gérer les opérations manuelles de la période.
        Permet de voir, valider et supprimer les opérations en brouillon.
        """
        self.ensure_one()

        # Créer une vue tree spéciale avec les actions
        return {
            'name': _('Gérer les opérations manuelles - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.cash.operation',
            'view_mode': 'tree,form',
            'views': [
                (self.env.ref('adi_treasury_enhanced.view_treasury_cash_operation_pending_tree').id, 'tree'),
                (False, 'form')
            ],
            'search_view_id': (self.env.ref('adi_treasury_enhanced.view_treasury_cash_operation_pending_search').id,),
            'domain': [
                ('cash_id', '=', self.cash_id.id),
                ('is_manual', '=', True),
                ('state', 'in', ['draft', 'posted']),
                '|',
                ('closing_id', '=', False),
                ('closing_id', '=', self.id),
            ],
            'context': {
                'default_cash_id': self.cash_id.id,
                'default_closing_id': self.id,
                'default_is_manual': True,
            },
            'target': 'current',
        }
