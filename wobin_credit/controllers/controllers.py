# -*- coding: utf-8 -*-
from odoo import http

# class WobinCredit(http.Controller):
#     @http.route('/wobin_credit/wobin_credit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wobin_credit/wobin_credit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wobin_credit.listing', {
#             'root': '/wobin_credit/wobin_credit',
#             'objects': http.request.env['wobin_credit.wobin_credit'].search([]),
#         })

#     @http.route('/wobin_credit/wobin_credit/objects/<model("wobin_credit.wobin_credit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wobin_credit.object', {
#             'object': obj
#         })