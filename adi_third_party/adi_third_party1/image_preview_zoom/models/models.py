# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class image_preview(models.Model):
#     _name = 'image_preview.image_preview'
#     _description = 'image_preview.image_preview'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

