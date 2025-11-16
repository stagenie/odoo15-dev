# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import math

# les valeur par defaut utilisé selon l'article 100 du CT

class DroitTimbre(models.Model):
    _name = 'droit.timbre'

    name = fields.Char(
        string="Nom",
        required=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        readonly=True,
        default=lambda self: self.env.company
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Currency",
        related='company_id.currency_id',
        help="Utility field to express amount currency"
    )

    tranche = fields.Monetary(
        string="Tranche",
        required=True,
        default=100.0,
    )

    prix = fields.Monetary(
        string="Prix",
        required=True,
        default=1.0,
    )

    # comptes de contreparties au ventes
    account_sale_id = fields.Many2one(
        comodel_name='account.account',
        string="Compte contrepartie lié au ventes"
    )

    # comptes de contreparties au achats
    account_purchase_id = fields.Many2one(
        comodel_name='account.account',
        string="Compte contrepartie lié au achats"
    )

    montant_min_valid = fields.Monetary(
        string="Montant minimum applicable",
        required=True,
        default=5.0,
        help="Le montant minimum pour application du droit de timbre"
    )

    montant_min = fields.Monetary(
        string="Montant minimum du timbre",
        required=True,
        default=5.0,
    )

    montant_max = fields.Monetary(
        string="Montant maximum du timbre",
        required=True,
        default=2500.0,
    )

    montant_arrondit = fields.Boolean(
        string='Arrondir le montant du timbre',
        default=False,
    )

    _sql_constraints = [(
        'company_id_uniq',
        'unique(company_id)',
        'Droit de Timbre (Timbre de quittances) doit être unique par société.'
    ),]

    @api.model
    def get_droit_timbre(self, company_id=False):
        droit_timbre_id = self or self.search([('company_id','=',company_id.id)], limit=1)

        if not droit_timbre_id:
            raise ValidationError(_('Veuillez configurer droit de timbre \
                (timbre de quittances) pour {}'.format(company_id.name)))

        return droit_timbre_id

    @api.model
    def get_montant_timbre(self, montant, company_id=False):
        if not montant: # ne rien faire si le montant est a 0
            return 0.0

        droit_timbre_id = self.get_droit_timbre(company_id)

        if montant < droit_timbre_id.montant_min_valid:
            raise ValidationError(_("Les sommes dont le montant n'excède pas {} {} ne donnent pas lieu à l'application du droit de timbre.".format(droit_timbre_id.montant_min_valid,
                                                                             droit_timbre_id.currency_id.symbol)))

        res = montant * droit_timbre_id.prix / droit_timbre_id.tranche

        # forcé l'utilisation des limite du droit de timbre
        # montant du droit de timbre rectifié
        if res < droit_timbre_id.montant_min:
            res = droit_timbre_id.montant_min
        elif res > droit_timbre_id.montant_max:
            res = droit_timbre_id.montant_max

        if droit_timbre_id.montant_arrondit:
            res = float(math.ceil(res))

        return res
