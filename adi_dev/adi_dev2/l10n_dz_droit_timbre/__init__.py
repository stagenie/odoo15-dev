# -*- encoding: utf-8 -*-

from . import models
from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    droit_timbre = env['droit.timbre'].search([])

    if not droit_timbre:
        account_id = env['account.account'].search([('code','=','445750')], limit=1).id # Droit de timbre perçus au profit du trésor
        for company_id in env['res.company'].search([]):
            env['droit.timbre'].create({
                'name': "Droit de timbre par defaut",
                'company_id': company_id.id,
                'account_sale_id': account_id,
                'account_purchase_id': account_id,
            })
