from odoo import fields, models, api
# from odoo.exceptions import UserError
from odoo.osv import expression


class AccountMove(models.Model):

    _inherit = "account.move"

    document_type_id = fields.Many2one(
        'account.document.type',
        'Document Type')
    document_number = fields.Char(
        string='Document Number')
    display_name = fields.Char()
