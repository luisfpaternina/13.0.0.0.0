from odoo import models, fields, api, _
from datetime import datetime, date
import logging

class PaymentReturnReason(models.Model):
    _inherit = 'payment.return.reason'

    is_generate_expense = fields.Boolean(
        string="Generate administrative expense")
