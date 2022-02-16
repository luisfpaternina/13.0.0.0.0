# -*- coding: utf-8 -*-
# from odoo import http


# class NybbleAccountPaymentReturnImportBbva(http.Controller):
#     @http.route('/nybble_account_payment_return_import__bbva/nybble_account_payment_return_import__bbva/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nybble_account_payment_return_import__bbva/nybble_account_payment_return_import__bbva/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('nybble_account_payment_return_import__bbva.listing', {
#             'root': '/nybble_account_payment_return_import__bbva/nybble_account_payment_return_import__bbva',
#             'objects': http.request.env['nybble_account_payment_return_import__bbva.nybble_account_payment_return_import__bbva'].search([]),
#         })

#     @http.route('/nybble_account_payment_return_import__bbva/nybble_account_payment_return_import__bbva/objects/<model("nybble_account_payment_return_import__bbva.nybble_account_payment_return_import__bbva"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nybble_account_payment_return_import__bbva.object', {
#             'object': obj
#         })
