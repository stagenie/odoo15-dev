from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CreateGlobalDelivery(models.TransientModel):
    _name = 'create.global.delivery'
    _description = 'Assistant de création de BL Global'

    date = fields.Date('Date', required=True, default=fields.Date.context_today)
    note = fields.Text('Note')
    picking_ids = fields.Many2many('stock.picking', string='Bons de livraison')
    partner_id = fields.Many2one('res.partner', 'Client', required=True)

    @api.model
    def default_get(self, fields):
        res = super(CreateGlobalDelivery, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        pickings = self.env['stock.picking'].browse(active_ids)
        
        # Vérifier si les BL sont en état 'done'
        if any(picking.state != 'done' for picking in pickings):
            raise UserError(_("Seuls les bons de livraison validés peuvent être regroupés"))
        
        if len(set(pickings.mapped('partner_id'))) > 1:
            raise UserError(_("Les bons de livraison doivent être du même client"))
            
        if any(picking.global_delivery_id for picking in pickings):
            raise UserError(_("Certains bons de livraison sont déjà inclus dans un BL global"))
            
        res.update({
            'picking_ids': [(6, 0, active_ids)],
            'partner_id': pickings[0].partner_id.id if pickings else False,
        })
        return res

    def action_create_global_delivery(self):
        lines = []
        for picking in self.picking_ids:
            for move in picking.move_lines:
                lines.append((0, 0, {
                    'product_id': move.product_id.id,
                    'quantity': move.quantity_done,
                    'uom_id': move.product_uom.id,
                }))
        
        global_delivery = self.env['global.delivery'].create({
            'date': self.date,
            'partner_id': self.partner_id.id,
            'note': self.note,
            'delivery_line_ids': lines,
            'picking_ids': [(6, 0, self.picking_ids.ids)],
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'global.delivery',
            'res_id': global_delivery.id,
            'view_mode': 'form',
            'target': 'current',
        }
# models/stock_picking.py


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    global_delivery_id = fields.Many2one('global.delivery', 'BL Global', readonly=True)

    def action_create_global_delivery(self):
        # Ne permettre que les BL en état 'done'
        if any(picking.state != 'done' for picking in self):
            raise UserError(_("Seuls les bons de livraison validés peuvent être regroupés"))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Créer BL Global'),
            'res_model': 'create.global.delivery',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_ids': self.ids}
        }