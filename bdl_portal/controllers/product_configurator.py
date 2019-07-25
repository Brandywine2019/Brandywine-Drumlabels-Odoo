# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
from odoo.addons.sale.controllers.product_configurator import ProductConfiguratorController


#class ProductConfiguratorController(ProductConfiguratorController):

    # @http.route(['/product_configurator/show_optional_products'], type='json', auth="user", methods=['POST'])
    # def show_optional_products(self, product_id, variant_values, pricelist_id, **kw):
    #     pricelist = self._get_pricelist(pricelist_id)
    #     result = self._show_optional_products(product_id, variant_values, pricelist, False, **kw)
    #     print('show optional products', result)
    #     return result
        
    # @http.route(['/product_configurator/optional_product_items'], type='json', auth="user", methods=['POST'])
    # def optional_product_items(self, product_id, pricelist_id, **kw):
    #     pricelist = self._get_pricelist(pricelist_id)
    #     result = self._optional_product_items(product_id, pricelist, **kw)
    #     print('optional product items', result)
    #     return result
    
    # @http.route(['/product_configurator/get_combination_info'], type='json', auth="user", methods=['POST'])
    # def get_combination_info(self, product_template_id, product_id, combination, add_qty, pricelist_id, **kw):
    #     combination = request.env['product.template.attribute.value'].browse(combination)
    #     pricelist = self._get_pricelist(pricelist_id)
    #     ProductTemplate = request.env['product.template']
    #     if 'context' in kw:
    #         ProductTemplate = ProductTemplate.with_context(**kw.get('context'))

    #     product_template = ProductTemplate.browse(int(product_template_id))
        
    #     res = product_template._get_combination_info(combination, int(product_id or 0), int(add_qty or 1), pricelist)
        
    #     if 'parent_combination' in kw:
    #         parent_combination = request.env['product.template.attribute.value'].browse(kw.get('parent_combination'))
    #         if not combination.exists() and product_id:
    #             product = request.env['product.product'].browse(int(product_id))
    #             if product.exists():
    #                 combination = product.product_template_attribute_value_ids
    #         res.update({
    #             'is_combination_possible': product_template._is_combination_possible(combination=combination, parent_combination=parent_combination),
    #         })

    #     if res.get('is_combination_possible') and not request.env.user.has_group('base.group_user'):
    #         res.update({'is_combination_possible': False})
    #     print('combination info', res)
    #     return res
