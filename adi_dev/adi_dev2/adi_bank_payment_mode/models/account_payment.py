from odoo import fields, models, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    mode_payment = fields.Selection( [
        ('check', 'Chèque'),
        ('bank_transfer', 'Virement bancaire'),
        ('bank_deposit', 'Versement bancaire')
    ], default = 'check',  string="Mode de paiement")

    check_number = fields.Char("Numéro de chèque")
    transfer_number = fields.Char("Numéro de virement")
    deposit_number = fields.Char("Numéro de versement")
    bank_type = fields.Char("Type")

    

    @api.onchange('journal_id')
    def _onchane_journal(self):
          if self.journal_id:             
             self.bank_type = self.journal_id.type
             if self.journal_id.type != 'bank':
                self.mode_payment = False
             else:
                self.mode_payment = 'check'

    @api.onchange('check_number')
    def _onchange_check_number(self):
        if self.check_number:
            self.ref=""
            self.ref = "CH N°:"+self.check_number

    @api.onchange('transfer_number')
    def _onchange_transfer_number(self):
        if self.transfer_number:
             self.ref=""
             self.ref = "Virement N°:" + self.transfer_number

    @api.onchange('deposit_number')
    def _onchange_deposit_number(self):
        if self.deposit_number:
            self.ref=""
            self.ref = "Versement N°:" + self.deposit_number


       
   
    @api.onchange('mode_payment')
    def _onchange_mode_payment(self):
        if self.mode_payment == 'check':
            self.check_number = False
        elif self.mode_payment == 'bank_transfer':
            self.transfer_number = False
        elif self.mode_payment == 'bank_deposit':
            self.deposit_number = False

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    mode_payment = fields.Selection( [
        ('check', 'Chèque'),
        ('bank_transfer', 'Virement bancaire'),
        ('bank_deposit', 'Versement bancaire')
    ], default = 'check',  string="Mode de paiement")

    check_number = fields.Char("Numéro de chèque")
    transfer_number = fields.Char("Numéro de virement")
    deposit_number = fields.Char("Numéro de versement")
    bank_type = fields.Char("Type")

    

    @api.onchange('journal_id')
    def _onchane_journal(self):
          if self.journal_id:             
             self.bank_type = self.journal_id.type
             if self.journal_id.type != 'bank':
                self.mode_payment = False
             else:
                self.mode_payment = 'check'
       
   
    @api.onchange('mode_payment')
    def _onchange_mode_payment(self):
        if self.mode_payment == 'check':
            self.check_number = False
        elif self.mode_payment == 'bank_transfer':
            self.transfer_number = False
        elif self.mode_payment == 'bank_deposit':
            self.deposit_number = False

    @api.onchange('check_number')
    def _onchange_check_number(self):
        if self.check_number:
            self.communication =""
            self.communication = "CH N°:"+self.check_number

    @api.onchange('transfer_number')
    def _onchange_transfer_number(self):
        if self.transfer_number:
             self.communication =""
             self.communication = "Virement N°:" + self.transfer_number

    @api.onchange('deposit_number')
    def _onchange_deposit_number(self):
        if self.deposit_number:
            self.communication =""
            self.communication = "Versement N°:" + self.deposit_number
    
    def _create_payment_vals_from_wizard(self):
        payment_vals = super()._create_payment_vals_from_wizard()
        payment_vals.update({
            'mode_payment': self.mode_payment,
            'check_number': self.check_number,
            'transfer_number': self.transfer_number,
            'deposit_number': self.deposit_number,
            'bank_type': self.bank_type,
            'ref':self.communication,
        })
        return payment_vals

       