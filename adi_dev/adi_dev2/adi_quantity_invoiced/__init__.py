# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID

from . import models


def force_recompute_qte_fields(cr, registry):
    """Fonction de post-installation pour forcer le recalcul des champs."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    ProductTemplate = env['product.template']
    ProductTemplate._force_recompute_qte_fields()




