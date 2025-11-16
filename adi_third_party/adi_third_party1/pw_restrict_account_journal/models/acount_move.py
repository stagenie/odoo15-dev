from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit = "account.move"



    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # Récupérer les journaux autorisés pour l'utilisateur actuel
        allowed_journals = self.env.user.journal_ids
        if allowed_journals:
            # Ajouter une restriction sur le champ journal_id
            args = args + [('journal_id', 'in', allowed_journals.ids)]
        # Appeler la méthode "search" d'origine avec les arguments modifiés
        return super(AccountMove, self).search(args, offset=offset, limit=limit, order=order, count=count)
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        # Récupérer les journaux autorisés pour l'utilisateur actuel
        allowed_journals = self.env.user.journal_ids
        if allowed_journals:
            # Ajouter une restriction sur le champ journal_id
            domain = domain + [('journal_id', 'in', allowed_journals.ids)]
        # Appeler la méthode "read_group" d'origine avec le domaine modifié
        return super(AccountMove, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)


 
    

