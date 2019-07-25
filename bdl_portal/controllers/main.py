# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from odoo.tools import ustr
from odoo.tools.pycompat import izip
from odoo import _, http
from odoo.addons.website.controllers.main import QueryURL

class WebsiteSale(WebsiteSale):

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
            additional_domain = self._get_domain_based_on_valid_product_tmpl_ids(self._valid_product_tmpl_ids_based_on_pricelist())
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

    # @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    # def product(self, product, category='', search='', **kwargs):
    #     if not product.can_access_from_current_website():
    #         raise NotFound()

    #     add_qty = int(kwargs.get('add_qty', 1))

    #     product_context = dict(request.env.context, quantity=add_qty,
    #                            active_id=product.id,
    #                            partner=request.env.user.partner_id)
    #     ProductCategory = request.env['product.public.category']

    #     if category:
    #         category = ProductCategory.browse(int(category)).exists()

    #     attrib_list = request.httprequest.args.getlist('attrib')
    #     attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
    #     attrib_set = {v[1] for v in attrib_values}

    #     keep = QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list)

    #     categs = ProductCategory.search([('parent_id', '=', False)])

    #     pricelist = request.website.get_current_pricelist()

    #     def compute_currency(price):
    #         return product.currency_id._convert(price, pricelist.currency_id, product._get_current_company(pricelist=pricelist, website=request.website), fields.Date.today())

    #     if not product_context.get('pricelist'):
    #         product_context['pricelist'] = pricelist.id
    #         product = product.with_context(product_context)

    #     # thie line is added by ehe
    #     valid_product_tmpl_ids = self._valid_product_tmpl_ids_based_on_pricelist()
            
    #     values = {
    #         'search': search,
    #         'category': category,
    #         'pricelist': pricelist,
    #         'attrib_values': attrib_values,
    #         # compute_currency deprecated, get from product
    #         'compute_currency': compute_currency,
    #         'attrib_set': attrib_set,
    #         'keep': keep,
    #         'categories': categs,
    #         'main_object': product,
    #         'product': product,
    #         'add_qty': add_qty,
    #         'optional_product_ids': [p.with_context({'active_id': p.id}) for p in product.optional_product_ids if p.id in valid_product_tmpl_ids],  # this line is modified to filter out invalid products based on our pricelist rule
    #         # get_attribute_exclusions deprecated, use product method
    #         'get_attribute_exclusions': self._get_attribute_exclusions,
    #     }
    #     return request.render("website_sale.product", values)

    
    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def address(self, new_billing=False, **kw):
        if not new_billing:
            print(kw)
            return super(WebsiteSale, self).address(**kw)

        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        print(request.website.user_id)
        print(partner_id)
        print(kw)
        print(new_billing)
        

        # IF PUBLIC ORDER
        if order.partner_id.id != request.website.user_id.sudo().partner_id.id and partner_id == -1:
            print('laaaaaaaaaaaaaaaaaaaaaaaaaaaaaa new billing')
            mode = ('new', 'billing')
            can_edit_vat = True
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        
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
                if mode[1] == 'billing':
                    order.partner_invoice_id = partner_id
                    # order.onchange_partner_id()
                    if not kw.get('use_same'):
                        kw['callback'] = kw.get('callback') or \
                            (not order.only_services and (mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(int(values['country_id']))
        country = country and country.exists() or def_country_id
        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
        }
        return request.render("website_sale.address", render_values)
