from odoo import models, fields, api, _

class PaymentReturnReason(models.Model):
    _inherit = 'payment.return.reason'

    # payment_mode_id = fields.Many2one(comodel_name='account.payment.mode', string='Payment Mode', required=True)
    payment_method_id = fields.Many2one(comodel_name='account.payment.method', string='Payment Method')
    payment_method_code = fields.Char(string='Payment Method Code', related='payment_method_id.code', readonly=True)

