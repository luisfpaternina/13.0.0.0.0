from odoo import fields, models, api, _

class AccountDocmentType(models.Model):
    _name = 'account.document.type'
    _description = 'Account Document Type'

    name = fields.Char(
        'Name',
        required=True)
