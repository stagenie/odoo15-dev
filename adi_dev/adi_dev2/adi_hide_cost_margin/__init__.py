# -*- coding: utf-8 -*-
from . import models


def _assign_cost_group_to_internal_users(cr, registry):
    """Assign 'Voir le Coût' group to all existing internal users at install."""
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    group_cost = env.ref('adi_hide_cost_margin.group_show_cost')
    group_internal = env.ref('base.group_user')
    internal_users = env['res.users'].search([('groups_id', 'in', [group_internal.id])])
    internal_users.write({'groups_id': [(4, group_cost.id)]})
