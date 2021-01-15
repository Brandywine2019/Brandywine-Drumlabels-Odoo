# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, tools

from odoo.http import request
from odoo.addons.website.models import ir_http

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    @api.multi
    def sale_get_order(self, force_create=False, code=None, update_pricelist=False, force_pricelist=False):
        self.ensure_one()
        sale_order_id = request.session.get('sale_order_id')
        partner = self.env.user.partner_id

        #assume there is order
        has_order = True
        if not sale_order_id:
            has_order = False

        res = super(Website, self).sale_get_order(force_create, code, update_pricelist, force_pricelist)

        # we know there was no order before super call
        if not has_order and res and partner:
            res.partner_invoice_id = partner
            res.partner_shipping_id = partner

        return res
