# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class CustomerPortal(CustomerPortal):
    
    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        if not request.env.user.has_group('base.group_user') and not request.env.user.has_group('bdl_portal.group_portal_admin'):
            values = {'access_denied': _('You do not have write access to account details.')}
            return request.render("portal.portal_my_details", values)
        else:
            return super(CustomerPortal, self).account(redirect, **post)
