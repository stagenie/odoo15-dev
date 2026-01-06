# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_reversal_entry = fields.Boolean(
        string='Est une ecriture de contre-passation',
        default=False,
        copy=False,
        help="Indique si cette ecriture a ete creee par contre-passation d'une ecriture orpheline"
    )
    reversed_entry_id = fields.Many2one(
        'account.move',
        string='Ecriture contre-passee',
        copy=False,
        readonly=True,
        help="Reference vers l'ecriture originale qui a ete contre-passee"
    )

    def action_create_reversal_entry(self):
        """
        Cree une ecriture de contre-passation pour annuler comptablement
        l'ecriture courante. Utilisee pour les ecritures orphelines.
        """
        self.ensure_one()

        if self.state != 'posted':
            raise UserError(_("Seules les ecritures validees peuvent etre contre-passees."))

        # Creer l'ecriture inverse
        reversal_move_vals = {
            'date': fields.Date.context_today(self),
            'journal_id': self.journal_id.id,
            'ref': _('Contre-passation de %s') % self.name,
            'is_reversal_entry': True,
            'reversed_entry_id': self.id,
            'move_type': 'entry',
            'line_ids': [],
        }

        # Inverser les lignes (debit <-> credit)
        for line in self.line_ids:
            reversal_move_vals['line_ids'].append((0, 0, {
                'account_id': line.account_id.id,
                'partner_id': line.partner_id.id,
                'name': _('Contre-passation: %s') % (line.name or self.name),
                'debit': line.credit,  # Inverser
                'credit': line.debit,  # Inverser
                'amount_currency': -line.amount_currency if line.amount_currency else 0.0,
                'currency_id': line.currency_id.id if line.currency_id else False,
                'analytic_account_id': line.analytic_account_id.id if line.analytic_account_id else False,
            }))

        # Creer et valider l'ecriture de contre-passation
        reversal_move = self.env['account.move'].create(reversal_move_vals)
        reversal_move.action_post()

        _logger.info(
            "Ecriture de contre-passation %s creee pour l'ecriture orpheline %s",
            reversal_move.name, self.name
        )

        return {
            'type': 'ir.actions.act_window',
            'name': _('Ecriture de contre-passation'),
            'res_model': 'account.move',
            'res_id': reversal_move.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_delete_with_move_lines(self):
        """
        Supprime l'ecriture comptable et toutes ses lignes.
        Utilisee pour les documents annules.
        ATTENTION: Operation irreversible!
        """
        for move in self:
            if move.state == 'posted':
                raise UserError(_(
                    "Impossible de supprimer l'ecriture %s car elle est validee. "
                    "Veuillez d'abord l'annuler."
                ) % move.name)

            _logger.warning(
                "Suppression de l'ecriture %s (ID: %s) et de ses %d lignes",
                move.name, move.id, len(move.line_ids)
            )

        # Supprimer les lignes d'abord (normalement cascade, mais par securite)
        self.mapped('line_ids').with_context(force_delete=True).unlink()
        # Puis supprimer les ecritures
        return super(AccountMove, self).unlink()
