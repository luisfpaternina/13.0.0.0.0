from odoo import fields, models, api
# from odoo.exceptions import UserError


class AccountDocmentType(models.Model):
    _name = 'account.document.type'
    _description = 'Account Document Type'
    _order = 'sequence, id asc'

    sequence = fields.Integer(
        default=10,
        required=True,
        help="Used to order records in tree views and relational fields"
    )
    name = fields.Char(
        'Name',
        required=True,
        index=True,
    )
