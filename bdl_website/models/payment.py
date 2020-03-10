# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare

import logging
import pprint

_logger = logging.getLogger(__name__)


class PaymentAcquirerPONumber(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('po_number', 'PO Number')])

    def po_number_get_form_action_url(self):
        return '/payment/po_number/feedback'


class PONumberPaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _po_number_form_get_tx_from_data(self, data):
        reference, amount, currency_name = data.get('reference'), data.get('amount'), data.get('currency_name')
        tx = self.search([('reference', '=', reference)])

        if not tx or len(tx) > 1:
            error_msg = _('received data for reference %s') % (pprint.pformat(reference))
            if not tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        return tx

    def _po_number_form_get_invalid_parameters(self, data):
        invalid_parameters = []

        if float_compare(float(data.get('amount') or '0.0'), self.amount, 2) != 0:
            invalid_parameters.append(('amount', data.get('amount'), '%.2f' % self.amount))
        if data.get('currency') != self.currency_id.name:
            invalid_parameters.append(('currency', data.get('currency'), self.currency_id.name))

        return invalid_parameters

    def _po_number_form_validate(self, data):
        _logger.info('Validated PO Number payment for tx %s: set as pending' % (self.reference))
        self._set_transaction_pending()
        return True


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Remove domain to show token that we saved earlier
    # Customer will always save tokens in website
    payment_token_id = fields.Many2one('payment.token', string="Saved payment token",
                                       domain="['|', ('acquirer_id.capture_manually', '=', False), ('partner_id', '=', partner_id)]",
                                       help="Note that tokens from acquirers set to only authorize transactions (instead of capturing the amount) are not available.")