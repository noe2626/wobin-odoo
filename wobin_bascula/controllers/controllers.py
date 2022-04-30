# -*- coding: utf-8 -*-
from odoo import http

# class WobinBascula(http.Controller):
#     @http.route('/wobin_bascula/wobin_bascula/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wobin_bascula/wobin_bascula/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wobin_bascula.listing', {
#             'root': '/wobin_bascula/wobin_bascula',
#             'objects': http.request.env['wobin_bascula.wobin_bascula'].search([]),
#         })

#     @http.route('/wobin_bascula/wobin_bascula/objects/<model("wobin_bascula.wobin_bascula"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wobin_bascula.object', {
#             'object': obj
#         })