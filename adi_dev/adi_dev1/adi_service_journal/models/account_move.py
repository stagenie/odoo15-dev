# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('is_service_invoice')
    def _onchange_is_service_invoice_journal(self):
        """
        Mettre à jour le domaine du journal et réinitialiser le journal
        si nécessaire lors du changement du type de facture service.
        """
        if self.move_type in ('in_invoice', 'in_refund'):
            # Vérifier si le journal actuel correspond au nouveau type
            if self.is_service_invoice:
                # Facture service: besoin d'un journal service
                if self.journal_id and not self.journal_id.is_service_journal:
                    # Chercher un journal service par défaut
                    service_journal = self.env['account.journal'].search([
                        ('type', '=', 'purchase'),
                        ('is_service_journal', '=', True),
                        ('company_id', '=', self.company_id.id),
                    ], limit=1)
                    if service_journal:
                        self.journal_id = service_journal
            else:
                # Facture normale: besoin d'un journal non-service
                if self.journal_id and self.journal_id.is_service_journal:
                    # Chercher un journal normal par défaut
                    normal_journal = self.env['account.journal'].search([
                        ('type', '=', 'purchase'),
                        ('is_service_journal', '=', False),
                        ('company_id', '=', self.company_id.id),
                    ], limit=1)
                    if normal_journal:
                        self.journal_id = normal_journal

    @api.onchange('is_service_invoice', 'move_type')
    def _onchange_service_invoice_journal_domain(self):
        """Retourner le domaine approprié pour le champ journal."""
        if self.move_type in ('in_invoice', 'in_refund'):
            domain = [('type', '=', 'purchase'), ('company_id', '=', self.company_id.id)]
            if self.is_service_invoice:
                domain.append(('is_service_journal', '=', True))
            else:
                domain.append(('is_service_journal', '=', False))
            return {'domain': {'journal_id': domain}}
        return {}

    @api.model
    def _search_default_journal(self, journal_types):
        """
        Surcharge pour prendre en compte le type service lors de la recherche
        du journal par défaut.
        """
        journal = super(AccountMove, self)._search_default_journal(journal_types)

        context = self._context or {}

        # Si on crée une facture fournisseur
        if 'purchase' in journal_types:
            # Si c'est une facture service
            if context.get('default_is_service_invoice'):
                service_journal = self.env['account.journal'].search([
                    ('type', '=', 'purchase'),
                    ('is_service_journal', '=', True),
                    ('company_id', '=', self.env.company.id),
                ], limit=1)
                if service_journal:
                    return service_journal
            else:
                # Facture normale: exclure les journaux service
                normal_journal = self.env['account.journal'].search([
                    ('type', '=', 'purchase'),
                    ('is_service_journal', '=', False),
                    ('company_id', '=', self.env.company.id),
                ], limit=1)
                if normal_journal:
                    return normal_journal

        return journal
