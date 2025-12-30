from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PartnerCreditLimitWizard(models.TransientModel):
    _name = 'partner.credit.limit.wizard'
    _description = 'Assistant de configuration limite crédit clients'

    # Filtres de sélection des clients
    filter_type = fields.Selection([
        ('all', 'Tous les clients'),
        ('with_credit', 'Clients avec limite de crédit active'),
        ('without_credit', 'Clients sans limite de crédit'),
        ('selected', 'Clients sélectionnés'),
    ], string="Filtre clients", default='all', required=True)

    # Paramètres à appliquer
    credit_limit_active = fields.Boolean(
        string="Activer la limite de crédit",
        default=True,
    )
    credit_limit = fields.Float(
        string="Montant limite de crédit",
        help="Laisser à 0 pour garder la limite existante de chaque client",
    )
    credit_limit_block_mode = fields.Selection([
        ('order', 'À la commande'),
        ('delivery', 'À la livraison'),
    ], string="Mode de blocage",
        default='delivery',
        required=True,
    )
    credit_limit_show_warning = fields.Boolean(
        string="Afficher avertissement",
        default=True,
        help="Afficher un message d'avertissement non bloquant sur la commande",
    )

    # Options de mise à jour
    update_limit = fields.Boolean(
        string="Mettre à jour le montant limite",
        default=False,
        help="Si coché, le montant limite sera mis à jour pour tous les clients sélectionnés",
    )
    update_block_mode = fields.Boolean(
        string="Mettre à jour le mode de blocage",
        default=True,
    )
    update_show_warning = fields.Boolean(
        string="Mettre à jour l'option d'avertissement",
        default=True,
    )

    # Clients sélectionnés (pour le mode 'selected')
    partner_ids = fields.Many2many(
        'res.partner',
        string="Clients sélectionnés",
    )

    # Clients à afficher (lecture seule, pour prévisualisation)
    preview_partner_ids = fields.Many2many(
        'res.partner',
        'wizard_preview_partner_rel',
        'wizard_id',
        'partner_id',
        string="Aperçu des clients",
        compute='_compute_preview_partners',
    )
    partner_count = fields.Integer(
        string="Nombre de clients",
        compute='_compute_preview_partners',
    )

    @api.depends('filter_type', 'partner_ids')
    def _compute_preview_partners(self):
        """Calcule la liste des clients qui seront affectés."""
        for wizard in self:
            partners = wizard._get_partners_to_update()
            wizard.preview_partner_ids = partners
            wizard.partner_count = len(partners)

    def _get_partners_to_update(self):
        """Retourne les clients à mettre à jour selon le filtre."""
        Partner = self.env['res.partner']
        domain = [('customer_rank', '>', 0)]  # Seulement les clients

        if self.filter_type == 'all':
            return Partner.search(domain)
        elif self.filter_type == 'with_credit':
            domain.append(('credit_limit_active', '=', True))
            return Partner.search(domain)
        elif self.filter_type == 'without_credit':
            domain.append(('credit_limit_active', '=', False))
            return Partner.search(domain)
        elif self.filter_type == 'selected':
            return self.partner_ids
        return Partner

    def action_preview(self):
        """Rafraîchit l'aperçu des clients."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_apply(self):
        """Applique les modifications aux clients sélectionnés."""
        partners = self._get_partners_to_update()

        if not partners:
            raise UserError(_("Aucun client à mettre à jour avec les filtres sélectionnés."))

        vals = {}

        # Toujours mettre à jour l'activation
        vals['credit_limit_active'] = self.credit_limit_active

        # Mettre à jour le montant limite si demandé
        if self.update_limit and self.credit_limit > 0:
            vals['credit_limit'] = self.credit_limit

        # Mettre à jour le mode de blocage si demandé
        if self.update_block_mode:
            vals['credit_limit_block_mode'] = self.credit_limit_block_mode

        # Mettre à jour l'option d'avertissement si demandé
        if self.update_show_warning:
            vals['credit_limit_show_warning'] = self.credit_limit_show_warning

        # Appliquer les modifications
        partners.write(vals)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Mise à jour effectuée'),
                'message': _('%d client(s) ont été mis à jour.') % len(partners),
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model
    def default_get(self, fields_list):
        """Pré-remplir avec les clients sélectionnés si appelé depuis une action."""
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            res['filter_type'] = 'selected'
            res['partner_ids'] = [(6, 0, active_ids)]
        return res
