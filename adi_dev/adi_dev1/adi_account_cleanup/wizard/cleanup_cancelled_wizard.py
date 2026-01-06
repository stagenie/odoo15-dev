# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CleanupCancelledWizard(models.TransientModel):
    _name = 'account.cleanup.cancelled.wizard'
    _description = 'Assistant de nettoyage des documents annules'

    # Options de nettoyage
    cleanup_type = fields.Selection([
        ('invoices', 'Factures annulees'),
        ('payments', 'Paiements annules'),
        ('all', 'Tous les documents annules'),
    ], string='Type de nettoyage', default='all', required=True)

    date_from = fields.Date(
        string='Date de debut',
        help="Filtrer les documents a partir de cette date (optionnel)"
    )
    date_to = fields.Date(
        string='Date de fin',
        help="Filtrer les documents jusqu'a cette date (optionnel)"
    )

    # Resultats de la recherche
    cancelled_invoice_ids = fields.Many2many(
        'account.move',
        'cleanup_wizard_invoice_rel',
        'wizard_id',
        'move_id',
        string='Factures annulees',
        readonly=True,
    )
    cancelled_payment_ids = fields.Many2many(
        'account.payment',
        'cleanup_wizard_payment_rel',
        'wizard_id',
        'payment_id',
        string='Paiements annules',
        readonly=True,
    )
    cancelled_move_ids = fields.Many2many(
        'account.move',
        'cleanup_wizard_move_rel',
        'wizard_id',
        'move_id',
        string='Ecritures annulees',
        readonly=True,
    )

    invoice_count = fields.Integer(
        string='Nombre de factures',
        compute='_compute_counts',
    )
    payment_count = fields.Integer(
        string='Nombre de paiements',
        compute='_compute_counts',
    )
    move_count = fields.Integer(
        string='Nombre d\'ecritures',
        compute='_compute_counts',
    )

    state = fields.Selection([
        ('draft', 'Configuration'),
        ('preview', 'Apercu'),
        ('done', 'Termine'),
    ], string='Etat', default='draft')

    confirm_delete = fields.Boolean(
        string='Je confirme vouloir supprimer definitivement ces documents',
        default=False,
    )

    @api.depends('cancelled_invoice_ids', 'cancelled_payment_ids', 'cancelled_move_ids')
    def _compute_counts(self):
        for wizard in self:
            wizard.invoice_count = len(wizard.cancelled_invoice_ids)
            wizard.payment_count = len(wizard.cancelled_payment_ids)
            wizard.move_count = len(wizard.cancelled_move_ids)

    def action_search_cancelled(self):
        """
        Recherche les documents annules selon les criteres selectionnes.
        """
        self.ensure_one()

        domain_invoice = [('state', '=', 'cancel'), ('move_type', 'in', ['out_invoice', 'out_refund', 'in_invoice', 'in_refund'])]
        domain_payment = []  # account.payment n'a pas de champ state dans Odoo 15
        domain_move = [('state', '=', 'cancel')]

        # Filtrer par date si specifie
        if self.date_from:
            domain_invoice.append(('date', '>=', self.date_from))
            domain_move.append(('date', '>=', self.date_from))
        if self.date_to:
            domain_invoice.append(('date', '<=', self.date_to))
            domain_move.append(('date', '<=', self.date_to))

        cancelled_invoices = self.env['account.move']
        cancelled_payments = self.env['account.payment']
        cancelled_moves = self.env['account.move']

        if self.cleanup_type in ('invoices', 'all'):
            cancelled_invoices = self.env['account.move'].search(domain_invoice)

        if self.cleanup_type in ('payments', 'all'):
            # Pour les paiements, on cherche les ecritures de paiement annulees
            payment_domain = [('state', '=', 'cancel'), ('payment_id', '!=', False)]
            if self.date_from:
                payment_domain.append(('date', '>=', self.date_from))
            if self.date_to:
                payment_domain.append(('date', '<=', self.date_to))
            cancelled_payment_moves = self.env['account.move'].search(payment_domain)
            cancelled_payments = cancelled_payment_moves.mapped('payment_id')

        if self.cleanup_type == 'all':
            # Toutes les ecritures annulees (hors factures et paiements deja comptes)
            all_cancelled = self.env['account.move'].search(domain_move)
            cancelled_moves = all_cancelled - cancelled_invoices - cancelled_payment_moves if self.cleanup_type == 'all' else all_cancelled

        self.write({
            'cancelled_invoice_ids': [(6, 0, cancelled_invoices.ids)],
            'cancelled_payment_ids': [(6, 0, cancelled_payments.ids)],
            'cancelled_move_ids': [(6, 0, cancelled_moves.ids)],
            'state': 'preview',
        })

        _logger.info(
            "Recherche terminee: %d factures, %d paiements, %d ecritures annulees",
            len(cancelled_invoices), len(cancelled_payments), len(cancelled_moves)
        )

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_delete_cancelled(self):
        """
        Supprime definitivement les documents annules selectionnes.
        ATTENTION: Operation IRREVERSIBLE!
        """
        self.ensure_one()

        if not self.confirm_delete:
            raise UserError(_(
                "Vous devez confirmer la suppression en cochant la case de confirmation."
            ))

        total_deleted = 0
        errors = []

        # Supprimer les factures annulees
        if self.cancelled_invoice_ids:
            try:
                count = len(self.cancelled_invoice_ids)
                # D'abord supprimer les lignes
                self.cancelled_invoice_ids.mapped('line_ids').with_context(force_delete=True).unlink()
                # Puis les factures
                self.cancelled_invoice_ids.with_context(force_delete=True).unlink()
                total_deleted += count
                _logger.info("Suppression de %d factures annulees", count)
            except Exception as e:
                errors.append(_("Erreur suppression factures: %s") % str(e))
                _logger.error("Erreur suppression factures: %s", str(e))

        # Supprimer les paiements annules (et leurs ecritures)
        if self.cancelled_payment_ids:
            try:
                count = len(self.cancelled_payment_ids)
                # Recuperer les ecritures liees
                payment_moves = self.cancelled_payment_ids.mapped('move_id')
                # Supprimer les lignes des ecritures
                payment_moves.mapped('line_ids').with_context(force_delete=True).unlink()
                # Supprimer les ecritures
                payment_moves.with_context(force_delete=True).unlink()
                # Supprimer les paiements
                self.cancelled_payment_ids.with_context(force_delete=True).unlink()
                total_deleted += count
                _logger.info("Suppression de %d paiements annules", count)
            except Exception as e:
                errors.append(_("Erreur suppression paiements: %s") % str(e))
                _logger.error("Erreur suppression paiements: %s", str(e))

        # Supprimer les autres ecritures annulees
        if self.cancelled_move_ids:
            try:
                count = len(self.cancelled_move_ids)
                self.cancelled_move_ids.mapped('line_ids').with_context(force_delete=True).unlink()
                self.cancelled_move_ids.with_context(force_delete=True).unlink()
                total_deleted += count
                _logger.info("Suppression de %d ecritures annulees", count)
            except Exception as e:
                errors.append(_("Erreur suppression ecritures: %s") % str(e))
                _logger.error("Erreur suppression ecritures: %s", str(e))

        self.state = 'done'

        message = _("%d documents supprimes definitivement.") % total_deleted
        if errors:
            message += "\n\n" + _("Erreurs rencontrees:") + "\n" + "\n".join(errors)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Nettoyage termine'),
                'message': message,
                'type': 'warning' if errors else 'success',
                'sticky': True,
            }
        }

    def action_view_cancelled_invoices(self):
        """Ouvre la liste des factures annulees."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Factures annulees'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.cancelled_invoice_ids.ids)],
            'context': {'create': False},
        }

    def action_view_cancelled_payments(self):
        """Ouvre la liste des paiements annules."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Paiements annules'),
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.cancelled_payment_ids.ids)],
            'context': {'create': False},
        }

    def action_view_cancelled_moves(self):
        """Ouvre la liste des ecritures annulees."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Ecritures annulees'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.cancelled_move_ids.ids)],
            'context': {'create': False},
        }

    def action_back_to_config(self):
        """Retourne a l'etape de configuration."""
        self.ensure_one()
        self.write({
            'state': 'draft',
            'cancelled_invoice_ids': [(5, 0, 0)],
            'cancelled_payment_ids': [(5, 0, 0)],
            'cancelled_move_ids': [(5, 0, 0)],
            'confirm_delete': False,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
