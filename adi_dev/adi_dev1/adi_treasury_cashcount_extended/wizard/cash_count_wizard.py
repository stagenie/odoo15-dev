# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class CashCountWizard(models.TransientModel):
    _name = 'cash.count.wizard'
    _description = 'Wizard de Comptage de Caisse'

    closing_id = fields.Many2one(
        'treasury.cash.closing',
        string='Clôture',
        required=True,
        readonly=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        related='closing_id.currency_id',
        readonly=True
    )

    line_ids = fields.One2many(
        'cash.count.wizard.line',
        'wizard_id',
        string='Lignes de comptage'
    )

    # Totaux
    total_bills = fields.Monetary(
        string='Total Billets',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True
    )

    total_coins = fields.Monetary(
        string='Total Pièces',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True
    )

    total_counted = fields.Monetary(
        string='Total Compté',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True
    )

    # Informations de référence
    balance_end_theoretical = fields.Monetary(
        string='Solde théorique',
        currency_field='currency_id',
        related='closing_id.balance_end_theoretical',
        readonly=True
    )

    difference = fields.Monetary(
        string='Écart',
        currency_field='currency_id',
        compute='_compute_difference',
        store=True
    )

    # Nombre de lignes remplies (pour validation)
    filled_lines_count = fields.Integer(
        string='Lignes remplies',
        compute='_compute_totals',
        store=True
    )

    @api.depends('line_ids.subtotal', 'line_ids.quantity', 'line_ids.denomination_type')
    def _compute_totals(self):
        """Calculer les totaux par type et le total général"""
        for wizard in self:
            total_bills = 0.0
            total_coins = 0.0
            filled_count = 0

            for line in wizard.line_ids:
                if line.quantity > 0:
                    filled_count += 1
                    if line.denomination_type == 'bill':
                        total_bills += line.subtotal
                    else:
                        total_coins += line.subtotal

            wizard.total_bills = total_bills
            wizard.total_coins = total_coins
            wizard.total_counted = total_bills + total_coins
            wizard.filled_lines_count = filled_count

    @api.depends('total_counted', 'balance_end_theoretical')
    def _compute_difference(self):
        """Calculer l'écart entre le total compté et le solde théorique"""
        for wizard in self:
            wizard.difference = wizard.total_counted - wizard.balance_end_theoretical

    @api.model
    def default_get(self, fields_list):
        """Charger les valeurs par défaut depuis la clôture"""
        res = super().default_get(fields_list)

        closing_id = self._context.get('active_id')
        if closing_id:
            closing = self.env['treasury.cash.closing'].browse(closing_id)
            res['closing_id'] = closing_id

        return res

    def _prepare_wizard_lines(self):
        """Préparer les lignes du wizard à partir des dénominations"""
        self.ensure_one()

        lines_data = []
        closing = self.closing_id

        # Récupérer les dénominations actives pour cette devise
        # Tri: Billets d'abord (bill < coin alphabétiquement, donc ASC), puis valeur décroissante
        denominations = self.env['cash.denomination'].search([
            ('currency_id', '=', closing.currency_id.id),
            ('active', '=', True)
        ], order='type asc, value desc')

        # Vérifier s'il y a déjà des lignes de comptage dans la clôture
        existing_counts = {
            line.denomination_id.id: line.quantity
            for line in closing.count_line_ids
        }

        for denomination in denominations:
            # Récupérer la quantité existante ou 0
            quantity = existing_counts.get(denomination.id, 0)

            lines_data.append((0, 0, {
                'denomination_id': denomination.id,
                'quantity': quantity,
            }))

        return lines_data

    @api.model
    def create(self, vals):
        """Créer le wizard et initialiser les lignes"""
        wizard = super().create(vals)

        # Initialiser les lignes
        if wizard.closing_id and not wizard.line_ids:
            wizard.line_ids = wizard._prepare_wizard_lines()

        return wizard

    def action_confirm(self):
        """Valider le comptage et mettre à jour la clôture"""
        self.ensure_one()

        closing = self.closing_id

        # Vérifier que la clôture est en brouillon
        if closing.state != 'draft':
            raise UserError(_(
                "Le comptage ne peut être modifié que pour une clôture en brouillon."
            ))

        # Note: On autorise le comptage à 0 (cas où la caisse est vide)
        # La validation du comptage obligatoire se fait via le flag cash_count_done

        # Supprimer les anciennes lignes de comptage
        closing.count_line_ids.unlink()

        # Créer les nouvelles lignes de comptage
        count_lines = []
        for line in self.line_ids:
            if line.quantity >= 0:  # Inclure les lignes à 0 pour garder l'historique
                count_lines.append((0, 0, {
                    'denomination_id': line.denomination_id.id,
                    'quantity': line.quantity,
                }))

        closing.write({
            'count_line_ids': count_lines,
            'balance_end_real': self.total_counted,
            'balance_end_real_manual': True,  # Marquer comme modifié manuellement
            'cash_count_done': True,  # Marquer le comptage comme effectué (même si total = 0)
        })

        # Message dans le chatter
        closing.message_post(
            body=_(
                "Comptage effectué via le wizard<br/>"
                "Total billets : %s %s<br/>"
                "Total pièces : %s %s<br/>"
                "<strong>Total compté : %s %s</strong><br/>"
                "Écart : %s %s"
            ) % (
                self.total_bills, self.currency_id.symbol,
                self.total_coins, self.currency_id.symbol,
                self.total_counted, self.currency_id.symbol,
                self.difference, self.currency_id.symbol
            )
        )

        return {'type': 'ir.actions.act_window_close'}

    def action_reset(self):
        """Réinitialiser toutes les quantités à 0"""
        self.ensure_one()

        for line in self.line_ids:
            line.quantity = 0

        # Retourner l'action pour rester sur le wizard
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cash.count.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self._context,
        }


class CashCountWizardLine(models.TransientModel):
    _name = 'cash.count.wizard.line'
    _description = 'Ligne de Comptage Wizard'
    _order = 'denomination_type asc, denomination_value desc'  # Billets d'abord, puis valeur décroissante

    wizard_id = fields.Many2one(
        'cash.count.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )

    denomination_id = fields.Many2one(
        'cash.denomination',
        string='Dénomination',
        required=True,
        ondelete='restrict'
    )

    denomination_value = fields.Monetary(
        string='Valeur',
        related='denomination_id.value',
        currency_field='currency_id',
        readonly=True
    )

    denomination_type = fields.Selection(
        related='denomination_id.type',
        string='Type',
        readonly=True
    )

    denomination_name = fields.Char(
        related='denomination_id.name',
        string='Nom',
        readonly=True
    )

    quantity = fields.Integer(
        string='Quantité',
        default=0
    )

    subtotal = fields.Monetary(
        string='Sous-total',
        currency_field='currency_id',
        compute='_compute_subtotal',
        store=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='wizard_id.currency_id',
        readonly=True
    )

    @api.depends('quantity', 'denomination_id.value')
    def _compute_subtotal(self):
        """Calculer le sous-total"""
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
                raise ValidationError(_(
                    "La quantité ne peut pas être négative !"
                ))
