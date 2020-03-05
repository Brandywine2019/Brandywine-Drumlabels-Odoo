# -*- coding: utf-8 -*-
import werkzeug
from odoo import http
from odoo.http import request
from odoo.addons.payment_stripe.controllers.main import StripeController
from odoo.addons.payment.controllers.portal import PaymentProcessing


class StripeController(StripeController):

    @http.route(['/payment/stripe/create_charge'], type='json', auth='public')
    def stripe_create_charge(self, **post):
        # res = super(StripeController, self).stripe_create_charge(**post)
        # Override the charge creation in the stripe payment controller
        print("WE reached inside the controller")
        TX = request.env['payment.transaction']
        tx = None
        if post.get('tx_ref'):
            tx = TX.sudo().search([('reference', '=', post['tx_ref'])])
        if not tx:
            tx_id = (post.get('tx_id') or request.session.get('sale_transaction_id') or
                     request.session.get('website_payment_tx_id'))
            tx = TX.sudo().browse(int(tx_id))
        if not tx:
            raise werkzeug.exceptions.NotFound()
        stripe_token = post['token']
        # response = None
        if tx.partner_id:
            payment_token_id = request.env['payment.token'].sudo().create({
                'acquirer_id': tx.acquirer_id.id,
                'partner_id': tx.partner_id.id,
                'stripe_token': stripe_token
            })
            tx.payment_token_id = payment_token_id

        # cancel the related payment transaction that was created
        # The transaction will be created on invoice(?)
        # tx._set_transaction_cancel()
        # Clean context and session
        # request.website.sale_reset()
        # Remove the tx from session
        # PaymentProcessing.remove_payment_transaction(tx)
        # request.session.update({
        #     'sale_order_id': False,
        #     'sale_last_order_id': False,
        #     'website_sale_current_pl': False,
        # })
        return '/shop/payment/validate_quote'

    # Mirror the existing /shop/payment/validate flow but we need to redirect differently
    @http.route('/shop/payment/validate_quote', type='http', auth="public", website=True, sitemap=False)
    def payment_validate_quote(self, transaction_id=None, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        if transaction_id:
            tx = request.env['payment.transaction'].sudo().browse(transaction_id)
            assert tx in order.transaction_ids()
        elif order:
            tx = order.get_portal_last_transaction()
        else:
            tx = None

        if not order or (order.amount_total and not tx):
            return request.redirect('/shop')

        if order and not order.amount_total and not tx:
            return request.redirect(order.get_portal_url())

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx and tx.state == 'draft':
            return request.redirect('/shop')

        PaymentProcessing.remove_payment_transaction(tx)
        return request.redirect('/shop/confirmation_quote')

    # Render a different order confirm page if we are using CC transactions with token
    @http.route(['/shop/confirmation_quote'], type='http', auth="public", website=True, sitemap=False)
    def payment_confirmation_quote(self, **post):
        """ End of checkout process controller. Confirmation is basically seing
        the status of a sale.order. State at this point :

         - should not have any context / session info: clean them
         - take a sale.order id, because we request a sale.order and are not
           session dependant anymore
        """
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            return request.render("bdl_website.confirmation_quote", {'order': order})
        else:
            return request.redirect('/shop')
