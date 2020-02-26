# -*- coding: utf-8 -*-
from odoo import http

# class BdlWebsite(http.Controller):
#     @http.route('/bdl_website/bdl_website/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bdl_website/bdl_website/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bdl_website.listing', {
#             'root': '/bdl_website/bdl_website',
#             'objects': http.request.env['bdl_website.bdl_website'].search([]),
#         })

#     @http.route('/bdl_website/bdl_website/objects/<model("bdl_website.bdl_website"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bdl_website.object', {
#             'object': obj
#         })