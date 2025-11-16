from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

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

    # Nouveaux champs pour les seuils
    montant_min_applicable = fields.Monetary(
        string="Montant minimum applicable",
        required=True,
        default=300.0,
        help="Montant minimum pour l'application du droit de timbre"
    )
    
    seuil_premiere_tranche = fields.Monetary(
        string="Seuil première tranche",
        required=True,
        default=30000.0,
        help="Seuil maximum pour la première tranche (1%)"
    )
    
    seuil_deuxieme_tranche = fields.Monetary(
        string="Seuil deuxième tranche",
        required=True,
        default=100000.0,
        help="Seuil maximum pour la deuxième tranche (1.5%)"
    )
    
    taux_premiere_tranche = fields.Float(
        string="Taux première tranche",
        required=True,
        default=0.01,
        help="Taux pour montants de 300 DA à 30 000 DA (1%)"
    )
    
    taux_deuxieme_tranche = fields.Float(
        string="Taux deuxième tranche",
        required=True,
        default=0.015,
        digits=(16, 3),  # 16 chiffres au total, dont 3 après la virgule
        help="Taux pour montants de 30 001 DA à 100 000 DA (1.5%)"
    )
    
    taux_troisieme_tranche = fields.Float(
        string="Taux troisième tranche",
        required=True,
        default=0.02,
        help="Taux pour montants supérieurs à 100 000 DA (2%)"
    )

    #  Les anciens Champs 
    montant_min = fields.Monetary(
        string="Montant minimum du timbre",
        required=True,
        default=5.0,
        help="Le montant minimum du droit de timbre"
    )
    montant_max = fields.Monetary(
        string="Montant maximum du timbre",
        required=True,
        default=2500.0,
    )
    montant_min_valid = fields.Monetary(
        string="Montant minimum applicable",
        required=True,
        default=5.0,
        help="Le montant minimum pour application du droit de timbre"
    )
    #########  
    
    montant_min_timbre = fields.Monetary(
        string="Montant minimum du timbre",
        required=True,
        default=5.0,
        help="Le montant minimum du droit de timbre"
    )

    #Attribuer un montant maximum du timbre
    with_max_timbre = fields.Boolean(
        string="Appliquer un montant maximum",
        default=False,
        help="Si coché, le montant du droit de timbre sera plafonné au montant maximum configuré"
    )

    montant_max_timbre = fields.Monetary(
        string="Montant maximum du timbre",
        default=100000.0,
        help="Montant maximum du droit de timbre si l'option est activée"
    )
    #
    account_sale_id = fields.Many2one(
        comodel_name='account.account',
        string="Compte contrepartie lié aux ventes"
    )
    
    account_purchase_id = fields.Many2one(
        comodel_name='account.account',
        string="Compte contrepartie lié aux achats"
    )

    _sql_constraints = [(
        'company_id_uniq',
        'unique(company_id)',
        'Droit de Timbre (Timbre de quittances) doit être unique par société.'
    )]

    @api.model
    def get_droit_timbre(self, company_id=False):
        droit_timbre_id = self or self.search([('company_id', '=', company_id.id)], limit=1)
        if not droit_timbre_id:
            raise ValidationError(_('Veuillez configurer droit de timbre \
                (timbre de quittances) pour {}'.format(company_id.name)))
        return droit_timbre_id

    @api.model
    def get_montant_timbre(self, montant, company_id=False, move_type=False):
        if not montant:  # ne rien faire si le montant est à 0
            return 0.0
            
        droit_timbre_id = self.get_droit_timbre(company_id)
        
        # Vérifier si le montant est inférieur au minimum applicable
        if montant < droit_timbre_id.montant_min_applicable:
            raise ValidationError(_(
                "Les sommes dont le montant n'excède pas {} {} ne donnent pas lieu à l'application du droit de timbre.".format(
                    droit_timbre_id.montant_min_applicable,
                    droit_timbre_id.currency_id.symbol
                )
            ))

        # Calcul du droit de timbre selon les tranches
        if montant <= droit_timbre_id.seuil_premiere_tranche:
            timbre = montant * droit_timbre_id.taux_premiere_tranche
        elif montant <= droit_timbre_id.seuil_deuxieme_tranche:
            timbre = montant * droit_timbre_id.taux_deuxieme_tranche
        else:
            timbre = montant * droit_timbre_id.taux_troisieme_tranche

        # Application du minimum si nécessaire
        if timbre < droit_timbre_id.montant_min_timbre:
            timbre = droit_timbre_id.montant_min_timbre

        # Application du maximum si l'option est activée
        if droit_timbre_id.with_max_timbre and timbre > droit_timbre_id.montant_max_timbre:
            timbre = droit_timbre_id.montant_max_timbre

        return timbre

