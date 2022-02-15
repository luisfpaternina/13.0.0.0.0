from odoo import fields, models, api
# from odoo.exceptions import UserError


class AccountDocmentType(models.Model):
    _name = 'account.document.type'
    _description = 'Account Document Type'

    sequence = fields.Integer()
    name = fields.Char(
        'Name',
        required=True)
