# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class TreasuryCashClosing(models.Model):
    _inherit = 'treasury.cash.closing'

    # =============================================
    # COMPTAGE INITIAL
    # =============================================

    # Activer le comptage initial
    use_initial_count = fields.Boolean(
        string='Utiliser le comptage initial',
        compute='_compute_use_initial_count',
        help="Indique si le comptage initial est activé"
    )

    # Forcer le comptage initial
    force_initial_count = fields.Boolean(
        string='Forcer le comptage initial',
        compute='_compute_force_initial_count',
        help="Indique si le comptage initial est obligatoire pour cette clôture"
    )

    # Indicateur si le comptage initial a été effectué
    initial_count_done = fields.Boolean(
        string='Comptage initial effectué',
        default=False,
        help="Indique si le comptage initial a été effectué via le wizard"
    )

    # Lignes de comptage initial
    initial_count_line_ids = fields.One2many(
        'treasury.cash.closing.initial.count',
        'closing_id',
        string='Comptage initial des billets et pièces',
        help="Détail du comptage initial par dénomination"
    )

    # Total du comptage initial
    initial_counted_total = fields.Monetary(
        string='Solde initial compté',
        currency_field='currency_id',
        compute='_compute_initial_counted_total',
        store=True,
        help="Montant total calculé à partir du comptage initial des billets et pièces"
    )

    # Écart initial
    initial_difference = fields.Monetary(
        string='Écart initial',
        currency_field='currency_id',
        compute='_compute_initial_difference',
        store=True,
        help="Différence entre le solde de départ théorique et le solde initial compté"
    )

    # =============================================
    # SOLDE DE DÉPART AJUSTÉ (Approche B)
    # =============================================

    balance_start_adjusted = fields.Monetary(
        string='Solde de départ ajusté',
        currency_field='currency_id',
        compute='_compute_balance_start_adjusted',
        store=True,
        help="Solde de départ utilisé pour le calcul du solde final théorique.\n"
             "Si le comptage initial a été effectué, c'est le solde initial compté.\n"
             "Sinon, c'est le solde de départ théorique."
    )

    # =============================================
    # MÉTHODES COMPUTE
    # =============================================

    @api.depends('cash_id.enable_initial_count')
    def _compute_use_initial_count(self):
        """Déterminer si le comptage initial est activé"""
        global_enable = self.env['ir.config_parameter'].sudo().get_param(
            'adi_treasury_cashcount_init.enable_initial_count', 'False'
        ) == 'True'

        for closing in self:
            closing.use_initial_count = global_enable or (
                closing.cash_id and closing.cash_id.enable_initial_count
            )

    @api.depends('cash_id.force_initial_count')
    def _compute_force_initial_count(self):
        """Déterminer si le forçage du comptage initial est actif"""
        global_force = self.env['ir.config_parameter'].sudo().get_param(
            'adi_treasury_cashcount_init.force_initial_count', 'False'
        ) == 'True'

        for closing in self:
            closing.force_initial_count = global_force or (
                closing.cash_id and closing.cash_id.force_initial_count
            )

    @api.depends('initial_count_line_ids.subtotal')
    def _compute_initial_counted_total(self):
        """Calculer le total initial à partir des lignes de comptage"""
        for closing in self:
            closing.initial_counted_total = sum(
                closing.initial_count_line_ids.mapped('subtotal')
            )

    @api.depends('balance_start', 'initial_counted_total', 'initial_count_done')
    def _compute_balance_start_adjusted(self):
        """
        Calculer le solde de départ ajusté (Approche B).

        Si le comptage initial a été effectué, on utilise le solde initial compté
        comme point de départ pour le calcul du solde théorique final.
        Sinon, on utilise le solde de départ théorique normal.
        """
        for closing in self:
            if closing.initial_count_done:
                # Utiliser le solde initial compté comme nouveau point de départ
                closing.balance_start_adjusted = closing.initial_counted_total
            else:
                # Pas de comptage initial, utiliser le solde théorique
                closing.balance_start_adjusted = closing.balance_start

    @api.depends('balance_start', 'initial_counted_total', 'initial_count_done')
    def _compute_initial_difference(self):
        """Calculer l'écart initial"""
        for closing in self:
            # L'écart est calculé seulement si le comptage a été effectué
            if closing.initial_count_done:
                closing.initial_difference = closing.initial_counted_total - closing.balance_start
            else:
                closing.initial_difference = 0.0

    @api.depends('balance_start_adjusted', 'total_in', 'total_out')
    def _compute_theoretical_balance(self):
        """
        Override pour utiliser le solde de départ ajusté (Approche B).

        Le solde théorique final est calculé en utilisant le solde de départ ajusté
        au lieu du solde de départ théorique. Cela permet de prendre en compte
        l'écart initial détecté lors du comptage d'ouverture.

        Formule: Solde théorique = Solde ajusté + Entrées - Sorties
        """
        for closing in self:
            closing.balance_end_theoretical = (
                closing.balance_start_adjusted + closing.total_in - closing.total_out
            )

            # SYNCHRONISATION AUTOMATIQUE après calcul du théorique
            if closing.state == 'draft':
                closing._sync_balance_end_real()

    # =============================================
    # ACTIONS WIZARD
    # =============================================

    def action_open_initial_count_wizard(self):
        """Ouvrir le wizard de comptage initial"""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_(
                "Le comptage initial ne peut être modifié que pour une clôture en brouillon."
            ))

        wizard = self.env['initial.cash.count.wizard'].create({
            'closing_id': self.id,
        })

        return {
            'name': _('Comptage Initial de Caisse'),
            'type': 'ir.actions.act_window',
            'res_model': 'initial.cash.count.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'active_model': 'treasury.cash.closing',
            }
        }

    # =============================================
    # OVERRIDE ACTIONS
    # =============================================

    def action_confirm(self):
        """Override pour vérifier le comptage initial obligatoire"""
        for closing in self:
            # Vérifier le comptage initial obligatoire
            if closing.force_initial_count and closing.use_initial_count:
                if not closing.initial_count_done:
                    raise ValidationError(_(
                        "Le comptage initial des billets et pièces est obligatoire.\n\n"
                        "Veuillez cliquer sur le bouton 'Comptage initial' à côté du champ "
                        "'Solde de départ' pour effectuer le comptage initial.\n\n"
                        "Note: Même si le solde est à 0, vous devez valider le wizard de comptage."
                    ))

        return super(TreasuryCashClosing, self).action_confirm()


class TreasuryCashClosingInitialCount(models.Model):
    """Ligne de comptage initial de clôture"""
    _name = 'treasury.cash.closing.initial.count'
    _description = 'Ligne de Comptage Initial de Clôture'
    _order = 'denomination_type asc, denomination_value desc'

    closing_id = fields.Many2one(
        'treasury.cash.closing',
        string='Clôture',
        required=True,
        ondelete='cascade',
        index=True
    )

    denomination_id = fields.Many2one(
        'cash.denomination',
        string='Dénomination',
        required=True,
        ondelete='restrict',
        domain="[('currency_id', '=', currency_id)]"
    )

    quantity = fields.Integer(
        string='Nombre',
        default=0,
        help="Nombre de billets ou pièces comptés"
    )

    subtotal = fields.Monetary(
        string='Sous-total',
        currency_field='currency_id',
        compute='_compute_subtotal',
        store=True,
        help="Quantité × Valeur de la dénomination"
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='closing_id.currency_id',
        store=True,
        readonly=True
    )

    denomination_value = fields.Monetary(
        string='Valeur unitaire',
        related='denomination_id.value',
        currency_field='currency_id',
        readonly=True
    )

    denomination_type = fields.Selection(
        related='denomination_id.type',
        string='Type',
        readonly=True,
        store=True
    )

    @api.depends('quantity', 'denomination_id.value')
    def _compute_subtotal(self):
        """Calculer le sous-total = quantité × valeur"""
        for line in self:
            if line.denomination_id and line.quantity:
                line.subtotal = line.quantity * line.denomination_id.value
            else:
                line.subtotal = 0.0

    @api.constrains('quantity')
    def _check_quantity_positive(self):
        """Vérifier que la quantité n'est pas négative"""
        for line in self:
            if line.quantity < 0:
                raise ValidationError(
                    _("La quantité ne peut pas être négative !")
                )
