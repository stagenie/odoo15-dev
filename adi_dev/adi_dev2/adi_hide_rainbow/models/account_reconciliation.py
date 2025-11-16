from odoo import models, api

class AccountReconciliation(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'

    @api.model
    def get_reconciliation_dict_from_model(self, model_id, domain=None):
        res = super().get_reconciliation_dict_from_model(model_id, domain=domain)
        
        # Masquer le "Rainbow Man" dans la vue de réconciliation
        res['show_mode_selector'] = False
        
        return res