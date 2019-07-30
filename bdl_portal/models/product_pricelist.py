# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from itertools import chain

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

from odoo.addons import decimal_precision as dp

from odoo.tools import pycompat


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    # this method returns a set of IDs of product template that are related to current pricelist
    def get_related_product_tmpl_ids(self):
        self.ensure_one()
        valid_ids = set()
        item_ids = self.item_ids
        if any(item_ids.filtered(lambda pli: pli.applied_on == '3_global')):
            # there is global so we can just return all since every product is included
            res = self.env['product.template'].search_read(domain=[], fields=['id'])
            return set([dic.get('id') for dic in res if dic.get('id')])
        if any(item_ids.filtered(lambda pli: pli.applied_on == '2_product_category')):
            categ_ids = item_ids.mapped('categ_id.id')
            res = self.env['product.template'].search_read(domain=[('categ_id', 'in', categ_ids)], fields=['id'])
            valid_ids |= set([dic.get('id') for dic in res if dic.get('id')])
        if any(item_ids.filtered(lambda pli: pli.applied_on == '1_product')):
            valid_ids |= set(item_ids.mapped('product_tmpl_id.id'))
        if any(item_ids.filtered(lambda pli: pli.applied_on == '0_product_variant')):
            valid_ids |= set(item_ids.mapped('product_id.product_tmpl_id.id'))
        return valid_ids

