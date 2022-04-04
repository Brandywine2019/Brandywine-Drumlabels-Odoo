# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    shipping_instructions = fields.Text('Shipping Instructions', track_visibility='onchange')

    def _check_carrier_quotation(self, force_carrier_id=None):
        # call Super to change delivery fee to 0.0
        res = super(SaleOrder, self)._check_carrier_quotation(force_carrier_id)
        delivery_line_ids = self.env['sale.order.line'].search([('order_id', 'in', self.ids), ('is_delivery', '=', True)])
        if delivery_line_ids:
            delivery_line_ids.write({
                'price_unit': 0.0
            })
        return res