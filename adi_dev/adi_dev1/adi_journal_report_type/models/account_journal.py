# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    invoice_report_type = fields.Selection([
        ('invoice', 'Facture'),
        ('sale', 'Vente'),
    ], string='Type de rapport',
       help="Détermine quel rapport d'impression sera disponible pour les factures de ce journal.\n"
            "- Facture: Affiche le bouton 'AB Facture'\n"
            "- Vente: Affiche les boutons 'Vente' et 'Vente TTC'")
