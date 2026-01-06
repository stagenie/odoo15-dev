# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class OrphanEntriesWizard(models.TransientModel):
    _name = 'account.orphan.entries.wizard'
    _description = 'Assistant de detection des ecritures orphelines'

    # Champs de resultat
    orphan_move_ids = fields.Many2many(
        'account.move',
        'orphan_wizard_move_rel',
        'wizard_id',
        'move_id',
        string='Ecritures orphelines detectees',
        readonly=True,
    )
    orphan_count = fields.Integer(
        string='Nombre d\'ecritures orphelines',
        compute='_compute_orphan_count',
    )
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('detected', 'Detecte'),
        ('done', 'Termine'),
    ], string='Etat', default='draft')

    # Lignes de detail
    line_ids = fields.One2many(
        'account.orphan.entries.wizard.line',
        'wizard_id',
        string='Detail des ecritures orphelines',
    )

    @api.depends('orphan_move_ids')
    def _compute_orphan_count(self):
        for wizard in self:
            wizard.orphan_count = len(wizard.orphan_move_ids)

    def action_detect_orphan_entries(self):
        """
        Detecte les ecritures orphelines dans la base de donnees.
        Une ecriture orpheline est une ecriture dont le libelle fait reference
        a un paiement qui n'existe plus dans la base.
        """
        self.ensure_one()

        # Rechercher les sequences de paiements utilisees
        # Pattern: C-XXX/YYYY/NNNN ou similaire
        cr = self.env.cr

        # Requete pour trouver les ecritures qui referencent des paiements supprimes
        # On cherche les ecritures de type 'entry' dont le libelle contient un numero
        # de paiement qui n'existe pas dans account_move
        # On exclut les ecritures de contre-passation (is_reversal_entry = TRUE)
        query = """
            WITH payment_patterns AS (
                -- Extraire les patterns de paiement des libelles
                SELECT DISTINCT
                    am.id as move_id,
                    am.name as move_name,
                    aml.name as line_name,
                    -- Extraire le pattern C-XXX/YYYY/NNNN du libelle
                    (regexp_matches(aml.name, '(C-[A-Z]+/[0-9]{4}/[0-9]+)', 'g'))[1] as payment_ref
                FROM account_move_line aml
                JOIN account_move am ON aml.move_id = am.id
                WHERE am.state = 'posted'
                  AND am.move_type = 'entry'
                  AND am.payment_id IS NULL
                  AND (am.is_reversal_entry IS NULL OR am.is_reversal_entry = FALSE)
                  AND aml.name ~ 'C-[A-Z]+/[0-9]{4}/[0-9]+'
                  AND aml.name NOT LIKE 'Contre-passation:%'
            )
            SELECT DISTINCT
                pp.move_id,
                pp.move_name,
                pp.payment_ref,
                pp.line_name
            FROM payment_patterns pp
            WHERE NOT EXISTS (
                SELECT 1 FROM account_move am2
                WHERE am2.name = pp.payment_ref
            )
            ORDER BY pp.move_name
        """

        cr.execute(query)
        results = cr.fetchall()

        if not results:
            self.state = 'detected'
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Detection terminee'),
                    'message': _('Aucune ecriture orpheline detectee.'),
                    'type': 'success',
                    'sticky': False,
                }
            }

        # Collecter les IDs des ecritures orphelines
        orphan_move_ids = list(set([r[0] for r in results]))

        # Creer les lignes de detail
        line_vals = []
        for move_id, move_name, payment_ref, line_name in results:
            line_vals.append((0, 0, {
                'move_id': move_id,
                'payment_reference': payment_ref,
                'line_name': line_name,
            }))

        self.write({
            'orphan_move_ids': [(6, 0, orphan_move_ids)],
            'line_ids': line_vals,
            'state': 'detected',
        })

        _logger.info(
            "Detection terminee: %d ecritures orphelines trouvees",
            len(orphan_move_ids)
        )

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_reverse_all_orphan_entries(self):
        """
        Contre-passe toutes les ecritures orphelines detectees.
        """
        self.ensure_one()

        if not self.orphan_move_ids:
            raise UserError(_("Aucune ecriture orpheline a contre-passer."))

        reversal_moves = self.env['account.move']
        errors = []

        for move in self.orphan_move_ids:
            try:
                result = move.action_create_reversal_entry()
                if result.get('res_id'):
                    reversal_moves |= self.env['account.move'].browse(result['res_id'])
            except Exception as e:
                errors.append(_("Erreur pour %s: %s") % (move.name, str(e)))
                _logger.error("Erreur lors de la contre-passation de %s: %s", move.name, str(e))

        self.state = 'done'

        message = _("%d ecritures de contre-passation creees.") % len(reversal_moves)
        if errors:
            message += "\n\n" + _("Erreurs rencontrees:") + "\n" + "\n".join(errors)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Contre-passation terminee'),
                'message': message,
                'type': 'warning' if errors else 'success',
                'sticky': True,
            }
        }

    def action_view_orphan_entries(self):
        """
        Ouvre la vue liste des ecritures orphelines detectees.
        """
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Ecritures orphelines'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.orphan_move_ids.ids)],
            'context': {'create': False},
        }


class OrphanEntriesWizardLine(models.TransientModel):
    _name = 'account.orphan.entries.wizard.line'
    _description = 'Ligne de detail des ecritures orphelines'

    wizard_id = fields.Many2one(
        'account.orphan.entries.wizard',
        string='Assistant',
        ondelete='cascade',
    )
    move_id = fields.Many2one(
        'account.move',
        string='Ecriture',
        readonly=True,
    )
    move_name = fields.Char(
        related='move_id.name',
        string='Numero',
        readonly=True,
    )
    move_date = fields.Date(
        related='move_id.date',
        string='Date',
        readonly=True,
    )
    payment_reference = fields.Char(
        string='Reference paiement manquant',
        readonly=True,
    )
    line_name = fields.Char(
        string='Libelle de la ligne',
        readonly=True,
    )
    amount = fields.Monetary(
        related='move_id.amount_total',
        string='Montant',
        readonly=True,
    )
    currency_id = fields.Many2one(
        related='move_id.currency_id',
        readonly=True,
    )

    def action_reverse_entry(self):
        """
        Contre-passe l'ecriture selectionnee.
        """
        self.ensure_one()
        return self.move_id.action_create_reversal_entry()

    def action_view_entry(self):
        """
        Ouvre l'ecriture en mode formulaire.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.move_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
