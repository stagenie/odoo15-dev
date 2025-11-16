# -*- encoding: utf-8 -*-

from . import models

from odoo import api, SUPERUSER_ID
import logging

def _preserve_tag_on_taxes(cr, registry):
    from odoo.addons.account.models.chart_template import preserve_existing_tags_on_taxes
    preserve_existing_tags_on_taxes(cr, registry, 'l10n_dz_scf')

def post_init_hook(cr, registry):
    _preserve_tag_on_taxes(cr, registry)

    # Compte de revenu de différence de caisse
    # Compte de dépenses des différences de caisse
    # ---> Faut les configurer manuellement dans res.company si besoin
    env = api.Environment(cr, SUPERUSER_ID, {})
    account_ids = env['account.account'].search([('code', '=like', '9%')])
    account_ids.unlink()