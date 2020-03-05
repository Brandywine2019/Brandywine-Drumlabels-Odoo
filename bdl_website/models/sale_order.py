# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_type = fields.Selection(string='Order Type', stored=True,
                                  selection=[('Credit Card', 'Credit Card'),
                                             ('Customer PO', 'Customer PO'),
                                             ('Signature Authorization', 'Signature Authorization')])

