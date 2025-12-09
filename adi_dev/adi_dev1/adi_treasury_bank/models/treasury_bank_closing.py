# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class TreasuryBankClosing(models.Model):
    _name = 'treasury.bank.closing'
    _description = 'Rapprochement Bancaire'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'closing_date desc, id desc'

    # Identification
    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau'),
        tracking=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        readonly=True,
        default=lambda self: self.env.company
    )

    # Compte bancaire
    bank_id = fields.Many2one(
        'treasury.bank',
        string='Compte bancaire',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        related='bank_id.currency_id',
        store=True,
        readonly=True
    )

    # Période
    closing_date = fields.Date(
        string='Date de clôture',
        required=True,
        default=fields.Date.context_today,
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True,
        help="Date de fin de la période à rapprocher"
    )
    period_start = fields.Date(
        string='Début de période',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True,
        help="Date de début de la période à rapprocher"
    )
    period_end = fields.Date(
        string='Fin de période',
        compute='_compute_period_end',
        store=True,
        readonly=True,
        help="Fin de la période (= date de clôture)"
    )

    # Soldes
    balance_start = fields.Monetary(
        string='Solde initial',
        required=True,
        currency_field='currency_id',
        readonly=True,
        tracking=True,
        help="Solde au début de la période (calculé automatiquement depuis la dernière clôture ou le solde d'ouverture)"
    )
    balance_end_theoretical = fields.Monetary(
        string='Solde final théorique',
        compute='_compute_theoretical_balance',
        store=True,
        currency_field='currency_id',
        help="Solde calculé à partir des opérations comptabilisées"
    )
    balance_end_bank = fields.Monetary(
        string='Solde final banque',
        currency_field='currency_id',
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True,
        help="Solde indiqué sur le relevé bancaire"
    )
    difference = fields.Monetary(
        string='Écart',
        compute='_compute_difference',
        store=True,
        currency_field='currency_id',
        help="Différence entre solde théorique et solde banque"
    )
    balance_end_bank_manual = fields.Boolean(
        string='Solde banque modifié manuellement',
        default=False,
        help="Indique si le solde banque a été saisi manuellement"
    )

    # Totaux
    total_in = fields.Monetary(
        string='Total entrées',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )
    total_out = fields.Monetary(
        string='Total sorties',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )

    # Relations
    operation_ids = fields.One2many(
        'treasury.bank.operation',
        'closing_id',
        string='Opérations',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    line_ids = fields.One2many(
        'treasury.bank.closing.line',
        'closing_id',
        string='Lignes de détail',
        readonly=True
    )

    # Rapprochement
    reconciled_operation_ids = fields.One2many(
        'treasury.bank.operation',
        compute='_compute_reconciled_operations',
        string='Opérations rapprochées'
    )
    unreconciled_operation_ids = fields.One2many(
        'treasury.bank.operation',
        compute='_compute_reconciled_operations',
        string='Opérations non rapprochées'
    )
    reconciled_count = fields.Integer(
        string='Nombre rapproché',
        compute='_compute_reconciliation_stats'
    )
    unreconciled_count = fields.Integer(
        string='Nombre non rapproché',
        compute='_compute_reconciliation_stats'
    )
    reconciliation_rate = fields.Float(
        string='Taux de rapprochement (%)',
        compute='_compute_reconciliation_stats'
    )

    # Opération d'ajustement
    adjustment_operation_id = fields.Many2one(
        'treasury.bank.operation',
        string='Opération d\'ajustement',
        readonly=True,
        help="Opération créée automatiquement en cas d'écart"
    )

    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('validated', 'Validé'),
        ('cancel', 'Annulé')
    ], string='État', default='draft', required=True,
        readonly=True, tracking=True)

    # Champs techniques
    user_id = fields.Many2one(
        'res.users',
        string='Créé par',
        default=lambda self: self.env.user,
        readonly=True
    )
    validated_by = fields.Many2one(
        'res.users',
        string='Validé par',
        readonly=True
    )
    validated_date = fields.Datetime(
        string='Date de validation',
        readonly=True
    )

    _sql_constraints = [
        ('date_check', 'check(period_start <= closing_date)',
         'La date de début doit être antérieure ou égale à la date de clôture !')
    ]

    @api.depends('closing_date')
    def _compute_period_end(self):
        """La fin de période est égale à la date de clôture"""
        for closing in self:
            closing.period_end = closing.closing_date

    @api.depends('balance_start', 'operation_ids', 'operation_ids.state',
                 'operation_ids.amount', 'operation_ids.operation_type')
    def _compute_theoretical_balance(self):
        """Calcule le solde théorique à partir des opérations"""
        for closing in self:
            balance = closing.balance_start

            # Calculer à partir des opérations comptabilisées
            for op in closing.operation_ids:
                if op.state in ['posted', 'reconciled']:
                    if op.operation_type == 'in':
                        balance += op.amount
                    else:
                        balance -= op.amount

            closing.balance_end_theoretical = balance

            # Synchroniser le solde banque si pas modifié manuellement
            if not closing.balance_end_bank_manual:
                closing.balance_end_bank = balance

    @api.depends('balance_end_theoretical', 'balance_end_bank')
    def _compute_difference(self):
        """Calcule l'écart entre théorique et banque"""
        for closing in self:
            closing.difference = closing.balance_end_bank - closing.balance_end_theoretical

    @api.depends('operation_ids', 'operation_ids.amount', 'operation_ids.operation_type',
                 'operation_ids.state')
    def _compute_totals(self):
        """Calcule les totaux d'entrées et sorties"""
        for closing in self:
            total_in = 0.0
            total_out = 0.0

            for op in closing.operation_ids:
                if op.state in ['posted', 'reconciled']:
                    if op.operation_type == 'in':
                        total_in += op.amount
                    else:
                        total_out += op.amount

            closing.total_in = total_in
            closing.total_out = total_out

    @api.depends('operation_ids', 'operation_ids.is_reconciled')
    def _compute_reconciled_operations(self):
        """Sépare les opérations rapprochées et non rapprochées"""
        for closing in self:
            reconciled = closing.operation_ids.filtered(lambda o: o.is_reconciled)
            unreconciled = closing.operation_ids.filtered(lambda o: not o.is_reconciled)

            closing.reconciled_operation_ids = reconciled
            closing.unreconciled_operation_ids = unreconciled

    @api.depends('operation_ids', 'operation_ids.is_reconciled')
    def _compute_reconciliation_stats(self):
        """Calcule les statistiques de rapprochement"""
        for closing in self:
            total = len(closing.operation_ids)
            reconciled = len(closing.operation_ids.filtered(lambda o: o.is_reconciled))

            closing.reconciled_count = reconciled
            closing.unreconciled_count = total - reconciled
            closing.reconciliation_rate = (reconciled / total * 100) if total > 0 else 0.0

    @api.model
    def create(self, vals):
        """Surcharge create pour générer la séquence et calculer la période"""
        # Générer la séquence
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'treasury.bank.closing') or _('Nouveau')

        # Calculer period_start si non fourni
        if 'period_start' not in vals and 'bank_id' in vals:
            bank = self.env['treasury.bank'].browse(vals['bank_id'])
            last_closing = self.search([
                ('bank_id', '=', bank.id),
                ('state', '=', 'validated')
            ], order='closing_date desc, id desc', limit=1)

            if last_closing:
                # Commencer le lendemain de la dernière clôture
                vals['period_start'] = last_closing.closing_date + timedelta(days=1)
            else:
                # Première clôture : demander à l'utilisateur ou mettre début du mois
                closing_date = vals.get('closing_date', fields.Date.context_today(self))
                if isinstance(closing_date, str):
                    closing_date = fields.Date.from_string(closing_date)
                vals['period_start'] = closing_date.replace(day=1)

        # Calculer balance_start automatiquement
        if 'bank_id' in vals:
            bank = self.env['treasury.bank'].browse(vals['bank_id'])
            last_closing = self.search([
                ('bank_id', '=', bank.id),
                ('state', '=', 'validated')
            ], order='closing_date desc, id desc', limit=1)

            if last_closing:
                # Utiliser le solde de fin de la dernière clôture validée
                vals['balance_start'] = last_closing.balance_end_bank
            else:
                # Première clôture : utiliser le solde d'ouverture du compte bancaire
                vals['balance_start'] = bank.opening_balance or 0.0

        # Vérifier qu'il n'y a pas déjà une clôture en cours
        if 'bank_id' in vals:
            existing = self.search([
                ('bank_id', '=', vals['bank_id']),
                ('state', 'in', ['draft', 'confirmed'])
            ], limit=1)
            if existing:
                raise ValidationError(_(
                    "Un rapprochement est déjà en cours pour ce compte bancaire.\n"
                    "Veuillez le terminer avant d'en créer un nouveau.\n"
                    "Référence: %s"
                ) % existing.name)

        closing = super(TreasuryBankClosing, self).create(vals)

        # Charger automatiquement les opérations
        closing.action_load_operations()

        return closing

    def write(self, vals):
        """Surcharge write pour marquer le solde banque comme modifié"""
        if 'balance_end_bank' in vals:
            vals['balance_end_bank_manual'] = True
        return super(TreasuryBankClosing, self).write(vals)

    def action_load_operations(self):
        """Charge les opérations de la période"""
        for closing in self:
            if closing.state != 'draft':
                raise UserError(_("Impossible de charger les opérations : le rapprochement n'est pas en brouillon."))

            # D'abord, synchroniser les paiements Odoo qui n'ont pas encore d'opération bancaire
            imported_count = closing._sync_payments_to_operations()

            # Rechercher les opérations de la période
            operations = self.env['treasury.bank.operation'].search([
                ('bank_id', '=', closing.bank_id.id),
                ('state', 'in', ['posted', 'reconciled']),
                ('date', '>=', closing.period_start),
                ('date', '<=', closing.closing_date),
                '|',
                ('closing_id', '=', False),
                ('closing_id', '=', closing.id)
            ])

            # Assigner les opérations à cette clôture
            operations.write({'closing_id': closing.id})

            # Recalculer les lignes de détail
            closing._compute_closing_lines()

            msg = _("%(count)d opération(s) chargée(s) pour la période du %(start)s au %(end)s") % {
                'count': len(operations),
                'start': closing.period_start,
                'end': closing.closing_date,
            }
            if imported_count > 0:
                msg += _("\n%(imported)d paiement(s) Odoo importé(s) automatiquement.") % {
                    'imported': imported_count
                }
            closing.message_post(body=msg)

    def _sync_payments_to_operations(self):
        """
        Synchronise les paiements Odoo avec les opérations bancaires.
        Crée les opérations manquantes pour les paiements validés dans la période.
        Retourne le nombre de paiements importés.
        """
        self.ensure_one()
        imported_count = 0

        # Chercher les paiements validés dans le journal associé à ce compte bancaire
        # qui n'ont pas encore d'opération bancaire
        payments = self.env['account.payment'].search([
            ('journal_id', '=', self.bank_id.journal_id.id),
            ('state', '=', 'posted'),
            ('date', '>=', self.period_start),
            ('date', '<=', self.closing_date),
            ('treasury_bank_operation_id', '=', False),
        ])

        for payment in payments:
            # Déterminer le type d'opération
            if payment.payment_type == 'inbound':
                operation_type = 'in'
            else:
                operation_type = 'out'

            # Déterminer la catégorie
            category = payment._get_bank_category(payment, operation_type)

            # Déterminer la méthode de paiement
            payment_method = payment._get_bank_payment_method(payment)

            # Créer l'opération bancaire
            operation = self.env['treasury.bank.operation'].create({
                'name': self.env['ir.sequence'].next_by_code('treasury.bank.operation'),
                'bank_id': self.bank_id.id,
                'operation_type': operation_type,
                'category_id': category.id if category else False,
                'amount': payment.amount,
                'date': payment.date,
                'value_date': payment.date,
                'description': payment.ref or payment.communication or _('Paiement %s') % payment.name,
                'partner_id': payment.partner_id.id if payment.partner_id else False,
                'payment_id': payment.id,
                'payment_method': payment_method,
                'bank_reference': payment.name,
                'is_manual': False,
                'state': 'posted',
            })

            # Lien bidirectionnel
            payment.treasury_bank_operation_id = operation.id
            imported_count += 1

        return imported_count

    def _compute_closing_lines(self):
        """Calcule les lignes de détail avec solde cumulé"""
        self.ensure_one()

        # Supprimer les lignes existantes
        self.line_ids.unlink()

        # Créer la ligne de solde initial
        lines_vals = [{
            'closing_id': self.id,
            'sequence': 0,
            'date': self.period_start,
            'operation_type': 'initial',
            'description': _('Solde initial'),
            'cumulative_balance': self.balance_start,
        }]

        # Trier les opérations de manière déterministe
        operations = self.operation_ids.filtered(
            lambda o: o.state in ['posted', 'reconciled']
        ).sorted(key=lambda o: (o.date, o.id))

        # Créer les lignes pour chaque opération
        cumulative_balance = self.balance_start
        sequence = 1

        for op in operations:
            # Calculer le nouveau solde cumulé
            if op.operation_type == 'in':
                cumulative_balance += op.amount
                amount_in = op.amount
                amount_out = 0.0
            else:
                cumulative_balance -= op.amount
                amount_in = 0.0
                amount_out = op.amount

            lines_vals.append({
                'closing_id': self.id,
                'sequence': sequence,
                'date': op.date,
                'operation_id': op.id,
                'partner_id': op.partner_id.id if op.partner_id else False,
                'category_id': op.category_id.id,
                'operation_type': op.operation_type,
                'description': op.description or op.category_id.name,
                'reference': op.bank_reference or op.name,
                'amount_in': amount_in,
                'amount_out': amount_out,
                'cumulative_balance': cumulative_balance,
                'is_reconciled': op.is_reconciled,
            })
            sequence += 1

        # Créer toutes les lignes
        self.env['treasury.bank.closing.line'].create(lines_vals)

    def action_confirm(self):
        """Confirme le rapprochement"""
        for closing in self:
            if closing.state != 'draft':
                raise UserError(_("Seuls les rapprochements en brouillon peuvent être confirmés."))

            # Vérifier qu'il y a au moins une opération
            if not closing.operation_ids:
                raise UserError(_("Impossible de confirmer : aucune opération chargée."))

            # Vérifier que le solde banque a été saisi
            if not closing.balance_end_bank and not closing.balance_end_bank_manual:
                raise UserError(_(
                    "Veuillez saisir le solde final indiqué sur le relevé bancaire "
                    "avant de confirmer le rapprochement."
                ))

            closing.write({'state': 'confirmed'})
            closing.message_post(body=_("Rapprochement confirmé"))

    def action_validate(self):
        """Valide le rapprochement"""
        for closing in self:
            if closing.state != 'confirmed':
                raise UserError(_("Seuls les rapprochements confirmés peuvent être validés."))

            # Vérifier s'il y a de nouveaux paiements non importés
            new_payments = closing._check_new_payments()
            if new_payments:
                raise UserError(_(
                    "Attention ! %(count)d nouveau(x) paiement(s) ont été enregistré(s) "
                    "dans la période mais ne sont pas inclus dans ce rapprochement.\n\n"
                    "Veuillez cliquer sur 'Charger opérations' pour les importer, "
                    "puis re-confirmer le rapprochement.\n\n"
                    "Paiements concernés :\n%(payments)s"
                ) % {
                    'count': len(new_payments),
                    'payments': '\n'.join(['- %s : %s %s' % (p.name, p.amount, p.currency_id.symbol) for p in new_payments[:10]]),
                })

            # Vérifier les opérations non rapprochées
            unreconciled_ops = closing.operation_ids.filtered(lambda o: not o.is_reconciled)
            if unreconciled_ops:
                raise UserError(_(
                    "Attention ! %(count)d opération(s) n'ont pas été rapprochée(s) "
                    "avec le relevé bancaire.\n\n"
                    "Cela peut créer des décalages dans votre suivi de trésorerie.\n\n"
                    "Opérations non rapprochées :\n%(operations)s\n\n"
                    "Veuillez soit :\n"
                    "- Cocher les opérations qui apparaissent sur votre relevé bancaire\n"
                    "- Ou utiliser le bouton 'Valider avec écarts' si vous souhaitez forcer la validation"
                ) % {
                    'count': len(unreconciled_ops),
                    'operations': '\n'.join(['- %s : %s %s (%s)' % (
                        op.name, op.amount, op.currency_id.symbol,
                        dict(op._fields['operation_type'].selection)[op.operation_type]
                    ) for op in unreconciled_ops[:10]]),
                })

            closing._do_validate()

    def action_validate_force(self):
        """Valide le rapprochement même avec des opérations non rapprochées"""
        for closing in self:
            if closing.state != 'confirmed':
                raise UserError(_("Seuls les rapprochements confirmés peuvent être validés."))

            # Vérifier s'il y a de nouveaux paiements non importés
            new_payments = closing._check_new_payments()
            if new_payments:
                raise UserError(_(
                    "Impossible de forcer la validation : %(count)d nouveau(x) paiement(s) "
                    "n'ont pas été importés.\n\n"
                    "Veuillez cliquer sur 'Charger opérations' puis re-confirmer."
                ) % {'count': len(new_payments)})

            # Avertissement dans le log
            unreconciled_ops = closing.operation_ids.filtered(lambda o: not o.is_reconciled)
            if unreconciled_ops:
                closing.message_post(
                    body=_("⚠️ Validation forcée avec %(count)d opération(s) non rapprochée(s)") % {
                        'count': len(unreconciled_ops)
                    }
                )

            closing._do_validate()

    def _check_new_payments(self):
        """Vérifie s'il y a de nouveaux paiements non importés dans la période"""
        self.ensure_one()
        return self.env['account.payment'].search([
            ('journal_id', '=', self.bank_id.journal_id.id),
            ('state', '=', 'posted'),
            ('date', '>=', self.period_start),
            ('date', '<=', self.closing_date),
            ('treasury_bank_operation_id', '=', False),
        ])

    def _do_validate(self):
        """Effectue la validation du rapprochement"""
        for closing in self:
            # Créer une opération d'ajustement si écart
            if closing.difference != 0:
                # Trouver la catégorie d'ajustement
                category = self.env['treasury.operation.category'].search([
                    ('code', '=', 'BANK_AJUST')
                ], limit=1)
                if not category:
                    category = self.env['treasury.operation.category'].search([
                        ('code', '=', 'AJUST')
                    ], limit=1)

                # Déterminer le type d'opération
                if closing.difference > 0:
                    operation_type = 'in'
                    amount = closing.difference
                else:
                    operation_type = 'out'
                    amount = -closing.difference

                # Créer l'opération d'ajustement (HORS clôture pour préserver l'historique)
                adjustment_op = self.env['treasury.bank.operation'].create({
                    'name': self.env['ir.sequence'].next_by_code('treasury.bank.operation'),
                    'bank_id': closing.bank_id.id,
                    'operation_type': operation_type,
                    'category_id': category.id if category else False,
                    'amount': amount,
                    'date': fields.Datetime.now(),
                    'value_date': closing.closing_date,
                    'description': _('Ajustement du rapprochement %s (écart: %.2f)') % (
                        closing.name, closing.difference
                    ),
                    'is_manual': False,
                    'state': 'posted',
                    'closing_id': False,  # HORS clôture !
                })

                closing.write({'adjustment_operation_id': adjustment_op.id})

                closing.message_post(
                    body=_("Opération d'ajustement créée pour un écart de %(amount).2f %(currency)s") % {
                        'amount': closing.difference,
                        'currency': closing.currency_id.symbol,
                    }
                )

            # Mettre à jour le compte bancaire
            closing.bank_id.write({
                'last_closing_date': closing.closing_date,
                'last_closing_balance': closing.balance_end_bank,
            })

            # Valider
            closing.write({
                'state': 'validated',
                'validated_by': self.env.user.id,
                'validated_date': fields.Datetime.now(),
            })

            closing.message_post(body=_("Rapprochement validé"))

    def action_back_to_draft(self):
        """Remet le rapprochement en brouillon"""
        for closing in self:
            # Vérifier qu'il n'y a pas de clôtures ultérieures validées
            later_closing = self.search([
                ('bank_id', '=', closing.bank_id.id),
                ('closing_date', '>', closing.closing_date),
                ('state', '=', 'validated')
            ], limit=1)

            if later_closing:
                raise UserError(_(
                    "Impossible de remettre en brouillon : "
                    "un rapprochement ultérieur est déjà validé (%s)."
                ) % later_closing.name)

            # Supprimer l'opération d'ajustement si elle existe
            if closing.adjustment_operation_id:
                closing.adjustment_operation_id.unlink()
                closing.write({'adjustment_operation_id': False})

            # Remettre en brouillon
            closing.write({
                'state': 'draft',
                'validated_by': False,
                'validated_date': False,
            })

            # Re-synchroniser le solde banque avec le théorique
            closing.write({
                'balance_end_bank': closing.balance_end_theoretical,
                'balance_end_bank_manual': False,
            })

            closing.message_post(body=_("Rapprochement remis en brouillon"))

    def action_cancel(self):
        """Annule le rapprochement"""
        for closing in self:
            if closing.state == 'validated':
                raise UserError(_("Impossible d'annuler un rapprochement validé. Utilisez 'Retour en brouillon'."))

            # Détacher les opérations
            closing.operation_ids.write({'closing_id': False})

            closing.write({'state': 'cancel'})
            closing.message_post(body=_("Rapprochement annulé"))

    def action_print_report(self):
        """Imprime le rapport de rapprochement"""
        self.ensure_one()
        return self.env.ref('adi_treasury_bank.action_report_bank_closing').report_action(self)


class TreasuryBankClosingLine(models.Model):
    _name = 'treasury.bank.closing.line'
    _description = 'Ligne de Rapprochement Bancaire'
    _order = 'sequence, id'

    closing_id = fields.Many2one(
        'treasury.bank.closing',
        string='Rapprochement',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(string='Séquence', default=10)
    date = fields.Datetime(string='Date')
    operation_id = fields.Many2one(
        'treasury.bank.operation',
        string='Opération',
        ondelete='cascade'
    )
    partner_id = fields.Many2one('res.partner', string='Partenaire')
    category_id = fields.Many2one('treasury.operation.category', string='Catégorie')
    operation_type = fields.Selection([
        ('initial', 'Solde initial'),
        ('in', 'Entrée'),
        ('out', 'Sortie')
    ], string='Type', required=True)
    description = fields.Text(string='Description')
    reference = fields.Char(string='Référence')
    amount_in = fields.Monetary(
        string='Entrée',
        currency_field='currency_id',
        default=0.0
    )
    amount_out = fields.Monetary(
        string='Sortie',
        currency_field='currency_id',
        default=0.0
    )
    cumulative_balance = fields.Monetary(
        string='Solde cumulé',
        currency_field='currency_id'
    )
    is_reconciled = fields.Boolean(
        string='Rapproché',
        default=False
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='closing_id.currency_id',
        store=True,
        readonly=True
    )
