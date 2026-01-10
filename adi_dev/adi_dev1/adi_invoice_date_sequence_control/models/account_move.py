# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _check_invoice_date_sequence(self):
        """
        Vérifie que la date de la facture est cohérente avec son numéro séquentiel.
        La date doit être supérieure ou égale à la date de la dernière facture validée
        dans le même journal.
        """
        # Récupérer les paramètres de configuration
        ICP = self.env['ir.config_parameter'].sudo()
        control_enabled = ICP.get_param(
            'adi_invoice_date_sequence_control.enabled', 'False'
        )
        application_date_str = ICP.get_param(
            'adi_invoice_date_sequence_control.application_date', False
        )

        # Si le contrôle n'est pas activé, on ne fait rien
        if control_enabled.lower() != 'true':
            return

        # Convertir la date d'application si elle existe
        application_date = False
        if application_date_str:
            try:
                application_date = fields.Date.from_string(application_date_str)
            except (ValueError, TypeError):
                application_date = False

        for move in self:
            # Ne contrôler que les factures et avoirs clients
            if move.move_type not in ('out_invoice', 'out_refund'):
                continue

            # Si la date de facture n'est pas définie, on ne peut pas contrôler
            if not move.invoice_date:
                continue

            # Si la date d'application est définie et que la date de la facture
            # est antérieure, on ne contrôle pas
            if application_date and move.invoice_date < application_date:
                continue

            # Rechercher la dernière facture validée dans le même journal
            # avec une date de facture définie
            last_invoice = self.search([
                ('journal_id', '=', move.journal_id.id),
                ('move_type', 'in', ('out_invoice', 'out_refund')),
                ('state', '=', 'posted'),
                ('invoice_date', '!=', False),
                ('id', '!=', move.id),
            ], order='invoice_date desc, name desc', limit=1)

            if last_invoice:
                # Si la date d'application est définie, ignorer les factures
                # antérieures à cette date pour la comparaison
                if application_date and last_invoice.invoice_date < application_date:
                    continue

                # Vérifier que la date est supérieure ou égale
                if move.invoice_date < last_invoice.invoice_date:
                    raise UserError(_(
                        "Erreur de cohérence Date/Séquence !\n\n"
                        "La date de la facture que vous essayez de valider "
                        "(%s) est antérieure à la date de la dernière facture "
                        "validée (%s - %s).\n\n"
                        "Pour maintenir la cohérence entre les numéros "
                        "séquentiels et les dates, la date de facturation "
                        "doit être supérieure ou égale à %s."
                    ) % (
                        move.invoice_date.strftime('%d/%m/%Y'),
                        last_invoice.name,
                        last_invoice.invoice_date.strftime('%d/%m/%Y'),
                        last_invoice.invoice_date.strftime('%d/%m/%Y'),
                    ))

    def action_post(self):
        """
        Surcharge de la méthode de validation pour ajouter le contrôle
        de cohérence date/séquence.
        """
        # Effectuer le contrôle avant la validation
        self._check_invoice_date_sequence()
        # Appeler la méthode parente
        return super(AccountMove, self).action_post()
