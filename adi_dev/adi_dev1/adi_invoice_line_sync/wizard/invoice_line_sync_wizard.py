# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class InvoiceLineSyncWizard(models.TransientModel):
    _name = 'invoice.line.sync.wizard'
    _description = 'Assistant d\'ajout de lignes depuis des factures'

    invoice_id = fields.Many2one(
        'account.move',
        string='Facture destination',
        required=True,
        readonly=True,
        default=lambda self: self.env.context.get('default_invoice_id')
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        related='invoice_id.partner_id',
        readonly=True
    )

    # Factures sources
    source_invoice_ids = fields.Many2many(
        'account.move',
        'invoice_sync_wizard_rel',
        'wizard_id',
        'invoice_id',
        string='Sélectionner les factures',
        help="Sélectionnez les factures dont vous voulez importer les lignes.",
        domain="[('id', '!=', invoice_id), ('partner_id', '=', partner_id), ('move_type', 'in', ['out_invoice', 'out_refund']), ('state', '=', 'posted')]"
    )

    line_count = fields.Integer(
        string='Nombre de lignes à ajouter',
        compute='_compute_line_count'
    )

    @api.depends('source_invoice_ids')
    def _compute_line_count(self):
        """Compte le nombre de lignes qui seront ajoutées"""
        for wizard in self:
            count = 0
            for invoice in wizard.source_invoice_ids:
                # Ne compter que les lignes produits (pas les sections/notes)
                count += len(invoice.invoice_line_ids.filtered(lambda l: not l.display_type))
            wizard.line_count = count

    def action_add_lines(self):
        """Ajoute les lignes des factures sélectionnées"""
        self.ensure_one()

        if not self.invoice_id:
            raise UserError(_('Aucune facture de destination.'))

        if not self.source_invoice_ids:
            raise UserError(_('Veuillez sélectionner au moins une facture.'))

        # Préparer les commandes pour ajouter les lignes
        line_commands = []
        lines_count = 0

        for source_invoice in self.source_invoice_ids:
            for source_line in source_invoice.invoice_line_ids:
                # Ne pas copier les sections/notes
                if source_line.display_type:
                    continue

                # Utiliser copy_data() pour copier correctement la ligne
                line_data = source_line.copy_data()[0]

                # Ajouter la référence à la facture source (pour traçabilité)
                line_data['source_invoice_id'] = source_invoice.id

                # Nettoyer les champs qui ne doivent pas être copiés
                for field in ['move_id', 'id', 'debit', 'credit', 'balance', 'amount_currency']:
                    line_data.pop(field, None)

                # Ajouter la commande de création
                line_commands.append((0, 0, line_data))
                lines_count += 1

        # Ajouter les lignes à la facture
        if line_commands:
            # Mettre à jour la facture avec les nouvelles lignes
            self.invoice_id.write({
                'invoice_line_ids': line_commands,
            })

            # Mettre à jour synced_invoice_ids pour traçabilité
            # Ajouter les nouvelles factures sources sans écraser les existantes
            existing_ids = self.invoice_id.synced_invoice_ids.ids
            new_ids = self.source_invoice_ids.ids
            all_ids = list(set(existing_ids + new_ids))

            self.invoice_id.write({
                'synced_invoice_ids': [(6, 0, all_ids)]
            })

        # Retourner une notification et fermer le wizard
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Lignes ajoutées'),
                'message': _('%d ligne(s) ajoutée(s) depuis %d facture(s).') % (
                    lines_count,
                    len(self.source_invoice_ids)
                ),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
