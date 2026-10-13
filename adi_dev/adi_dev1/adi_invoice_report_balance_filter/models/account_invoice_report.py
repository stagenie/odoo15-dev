from odoo import models, fields, api


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    # Rapatrie le champ de la facture (account.move) dans la vue SQL d'analyse,
    # afin de pouvoir filtrer l'Analyse de Facture comme les Factures Clients.
    exclude_from_partner_ledger = fields.Boolean(
        string="Hors solde",
        readonly=True,
        help="Vrai si la facture est exclue du calcul du solde (Partner Ledger).",
    )

    @api.model
    def _select(self):
        # account_move est déjà joint sous l'alias "move" dans _from().
        return super()._select() + \
            ", COALESCE(move.exclude_from_partner_ledger, FALSE) AS exclude_from_partner_ledger"
