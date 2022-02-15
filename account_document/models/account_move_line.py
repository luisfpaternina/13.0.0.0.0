from odoo import fields, models, api, _
import logging

class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    @api.onchange('product_id')
    def _change_account(self):
        for record in self:
            if record.product_id:
                record.account_id = record.move_id.journal_id.default_debit_account_id.id
