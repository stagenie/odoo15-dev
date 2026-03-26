from odoo import models, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def unlink(self):
        if not self.env.user.has_group('adi_restrict_payment_delete.group_delete_payment'):
            raise UserError(_("Vous n'êtes pas autorisé à supprimer des paiements. "
                              "Contactez votre administrateur."))
        return super().unlink()
