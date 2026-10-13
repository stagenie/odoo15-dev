from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Adresse complète du client, affichée à la sélection du partenaire dans le devis.
    partner_full_address = fields.Char(
        string='Adresse client',
        related='partner_id.contact_address',
        readonly=True,
        help="Adresse complète (formatée) du client sélectionné."
    )
