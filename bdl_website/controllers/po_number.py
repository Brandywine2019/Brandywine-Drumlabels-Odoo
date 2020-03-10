# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PONumberController(http.Controller):
    _accept_url = '/payment/po_number/feedback'

    @http.route([
        '/payment/po_number/feedback',
    ], type='http', auth='none', csrf=False)
    def transfer_form_feedback(self, **post):
        _logger.info('Beginning form_feedback with post data %s', pprint.pformat(post))  # debug
        request.env['payment.transaction'].sudo().form_feedback(post, 'po_number')
        return werkzeug.utils.redirect('/payment/process')
