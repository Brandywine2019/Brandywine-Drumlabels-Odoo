# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PONumberController(http.Controller):
    _accept_url = '/payment/po_number/feedback'

    @http.route(['/payment/po_number'], type='json', auth='public')
    def set_po_num_sale(self, po_num):
        sale_order_id = request.session.get('sale_order_id')
        if not sale_order_id:
            return False
        sale_order = request.env['sale.order'].sudo().browse(sale_order_id).exists() if sale_order_id else None
        if sale_order:
            sale_order.order_type = 'Customer PO'
            sale_order.client_order_ref = po_num
        else:
            return False
        return True

    @http.route([
        '/payment/po_number/feedback',
    ], type='http', auth='none', csrf=False)
    def transfer_form_feedback(self, **post):
        _logger.info('Beginning form_feedback with post data %s', pprint.pformat(post))  # debug
        request.env['payment.transaction'].sudo().form_feedback(post, 'po_number')
        return werkzeug.utils.redirect('/payment/process')
