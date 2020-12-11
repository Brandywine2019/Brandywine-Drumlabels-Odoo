# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from odoo.tools import ustr
from odoo.tools.pycompat import izip
from odoo import _, http
from odoo.addons.website.controllers.main import QueryURL


class WebsiteSale(WebsiteSale):

    ####################################################
    # products by pricelist to current request env user 
    ###################################################

    def _valid_product_tmpl_ids_based_on_pricelist(self):
        # when user is public, they should see only products that are included in the public pricelist
        pricelist_id = request.env.ref('product.list0')
        if not request.env.user._is_public() and request.env.user.partner_id and request.env.user.partner_id.property_product_pricelist:
            pricelist_id = request.env.user.partner_id.property_product_pricelist
        return pricelist_id.get_related_product_tmpl_ids()  # this is a set of ids, not objects

    def _get_domain_based_on_valid_product_tmpl_ids(self, valid_set, product_type='product.template'):
        if product_type == 'product.template':
            domain = [('id', 'in', list(valid_set))]
        elif product_type == 'product.product':
            domain = [('product_tmpl_id', 'in', list(valid_set))]
        else:
            domain = []
        return domain

    def _get_search_domain(self, search, category, attrib_values):
        domain = super(WebsiteSale, self)._get_search_domain(search, category, attrib_values)

        if not request.env.user.has_group('base.group_user'):
            additional_domain = self._get_domain_based_on_valid_product_tmpl_ids(
                self._valid_product_tmpl_ids_based_on_pricelist())
            if additional_domain:
                domain += additional_domain
        return domain

    def _cart_accessories(self):
        products = super(WebsiteSale, self)._cart_accessories()
        # products is a list of products
        if not request.env.user.has_group('base.group_user'):
            valid_product_tmpl_ids = self._valid_product_tmpl_ids_based_on_pricelist()
            return [product for product in products if product.product_tmpl_id.id in valid_product_tmpl_ids]
        else:
            return products

    #####################################
    # billing address editing and adding
    #####################################

    # Create the domain for the address search
    def _get_address_domain(self, search):
        domain = []
        if search:
            for srch in search.split(" "):
                domain += [
                    '|', '|', '|', '|', ('name', 'ilike', srch), ('street', 'ilike', srch),
                    ('street2', 'ilike', srch), ('city', 'ilike', srch), ('zip', 'ilike', srch),
                ]
        return domain

    # modify checkout values so that billing contacts are displayed just as shipping
    def checkout_values(self, **kw):
        values = super(WebsiteSale, self).checkout_values(**kw)
        order = request.website.sale_get_order()  # no need to force create since it was created in the super
        billings = []
        shippings = []

        # Handle case where user is only Client User and not admin
        if not request.env.user.has_group('bdl_portal.group_portal_admin'):
            order.partner_invoice_id = order.partner_id
            order.partner_shipping_id = order.partner_id
            values.update({
                'shippings': [order.partner_id],
                'billings': [order.partner_id],
            })
            return values

        if order.partner_id != request.website.user_id.sudo().partner_id:
            Partner = order.partner_id.with_context(show_address=1).sudo()

            # Change shipping addresses by changing domain and resetting shippings
            # (child of commercial id and of type delivery) OR parent contact OR current contact

            ship_search = kw.get('ship_search', [])
            ship_domain = self._get_address_domain(ship_search)
            shippings = Partner.search([
                '|', '|', '&', ("id", "child_of", order.partner_id.commercial_partner_id.ids),
                ("type", "in", ["delivery"]), ("id", "=", order.partner_id.parent_id.id), ("id", "=", order.partner_id.id)
            ] + ship_domain, limit=6, order='id desc')

            if shippings:
                if kw.get('partner_id') or 'use_billing' in kw:
                    if 'use_billing' in kw:
                        partner_id = order.partner_id.id
                    else:
                        partner_id = int(kw.get('partner_id'))
                    if partner_id in shippings.mapped('id'):
                        order.partner_shipping_id = partner_id
                elif not order.partner_shipping_id:
                    last_order = request.env['sale.order'].sudo().search([("partner_id", "=", order.partner_id.id)],
                                                                         order='id desc', limit=1)
                    order.partner_shipping_id.id = last_order and last_order.id

                # Make sure the current shipping address is in the available ship results
                if order.partner_shipping_id not in shippings:
                    shippings = shippings[:-1] + order.partner_shipping_id
                    # set to the first address in shippings

            # Billing with filter for invoice type and parent contact only
            # (A AND B) OR (C)
            # OR (A AND B) (C)
            # OR (AND A B) (C)
            # OR AND A B C
            # (child of commercial id and of type invoice) OR parent contact
            bill_search = kw.get('bill_search', [])
            bill_domain = self._get_address_domain(bill_search)
            # billings = Partner.search(search_domain)
            billings = Partner.search([
                '|', '|', '&', ("id", "child_of", order.partner_id.commercial_partner_id.ids),
                ("type", "in", ["invoice"]), ("id", "=", order.partner_id.parent_id.id), ("id", "=", order.partner_id.id),
                # '|', ("type", "in", ["invoice"]), ("id", "=", order.partner_id.commercial_partner_id.id)
                # original line below
                # '|', ("type", "in", ["invoice", "contact"]), ("id", "=", order.partner_id.commercial_partner_id.id)
            ] + bill_domain, limit=6, order='id desc')
            if billings:
                if kw.get('partner_id'):
                    partner_id = int(kw.get('partner_id'))
                    if partner_id in billings.mapped('id'):
                        order.partner_invoice_id = partner_id
                # Make sure the current billing address is in the available bill results
                if order.partner_invoice_id not in billings:
                    # set to the first address in billings
                    billings = billings[:-1] + order.partner_invoice_id

            values.update({'bill_search': bill_search,
                           'ship_search': ship_search})

        values.update({'billings': billings,
                       'shippings': shippings})

        if not order.partner_id.user_ids.filtered(
                lambda current_user: current_user.has_group('bdl_portal.group_portal_admin') or current_user.has_group(
                        'base.group_user') or current_user.has_group('base.group_public')):
            values.update({
                'shippings': [order.partner_shipping_id or order.partner_id],
                'billings': [order.partner_invoice_id or order.partner_id],
            })
        return values

    def _checkout_form_save(self, mode, checkout, all_values):
        Partner = request.env['res.partner']
        partner_id = False
        if mode == ('add', 'billing'):
            partner_id = int(all_values.get('partner_id', 0))
            if partner_id:
                partner_invoice_id = False
                # this means we have to create a new billing address
                if partner_id == -1:
                    partner_invoice_id = Partner.sudo().create(checkout).id
                else:
                    partner_invoice_id = partner_id
                    Partner.browse(partner_invoice_id).sudo().write(checkout)  # update our existing invoice
                # order = request.website.sale_get_order()
                # order.sudo().write({'partner_invoice_id': partner_invoice_id})
        else:
            partner_id = super(WebsiteSale, self)._checkout_form_save(mode, checkout, all_values)
        return partner_id

    def values_postprocess(self, order, mode, values, errors, error_msg):
        values, errors, error_msg = super(WebsiteSale, self).values_postprocess(order, mode, values, errors, error_msg)
        if mode == ('add', 'billing'):
            values.update({'type': 'invoice', 'parent_id': order.partner_id.commercial_partner_id.id})
        return values, errors, error_msg

    @http.route(['/shop/address_add_billing'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def address_add_billing(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = ('add', 'billing')
        country_code = request.session['geoip'].get('country_code')
        def_country_id = False
        if country_code:
            def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
        else:
            def_country_id = request.website.user_id.sudo().country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))
        if partner_id and partner_id != -1:
            values = Partner.browse(partner_id)

        # IF POSTED
        if 'submitted' in kw:

            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)

                if mode[0] == 'add' and partner_id and partner_id != -1:
                    order.partner_invoice_id = partner_id
                    # print(order.partner_id, order.partner_invoice_id)
                    # order.partner_id = partner_id
                # order.onchange_partner_id()
                if not kw.get('use_same'):
                    kw['callback'] = kw.get('callback') or \
                                     (not order.only_services and (mode[0] in ['edit',
                                                                               'add'] and '/shop/checkout' or '/shop/address_add_billing'))
                order.message_partner_ids = [(4, partner_id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(
            int(values['country_id']))
        country = country and country.exists() or def_country_id
        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': True,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
            'add_billing': 1,

        }
        return request.render("website_sale.address", render_values)

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def address(self, **kw):
        if not kw.get('add_billing'):
            return super(WebsiteSale, self).address(**kw)
        else:
            return self.address_add_billing(**kw)

    # By passing the direct to confirm cart in checkout
    # Always redirect to address, no express
    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        if post.get('express'):
            order = request.website.sale_get_order()
            values = self.checkout_values(**post)
            values.update({'website_sale_order': order})
            return request.render("website_sale.checkout", values)
        else:
            return super(WebsiteSale, self).checkout(**post)

    @http.route(['/payment/ship_instructions'], type='json', auth='public')
    def set_po_num_sale(self, ship_instructions):
        sale_order_id = request.session.get('sale_order_id')
        if not sale_order_id:
            return False
        sale_order = request.env['sale.order'].sudo().browse(sale_order_id).exists() if sale_order_id else None
        if sale_order:
            sale_order.shipping_instructions = ship_instructions
        else:
            return False
        return True
