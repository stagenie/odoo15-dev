from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_limit_block_mode = fields.Selection([
        ('order', 'À la commande'),
        ('delivery', 'À la livraison'),
    ], string="Blocage limite crédit",
        default='delivery',
        help="Définit le moment où le blocage sera appliqué si la limite de crédit est dépassée:\n"
             "- À la commande: Blocage lors de la confirmation de la commande de vente\n"
             "- À la livraison: Blocage lors de la validation du bon de livraison"
    )

    credit_limit_show_warning = fields.Boolean(
        string="Afficher avertissement",
        default=True,
        help="Si activé, affiche un message d'avertissement non bloquant sur la commande "
             "lorsque le client approche ou dépasse sa limite de crédit."
    )
