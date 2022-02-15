from odoo import fields, models, api, _
import logging

class AccountMoveLine(models.Model):

    _inherit = "account.move.line"
