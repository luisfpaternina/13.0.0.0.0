from odoo import fields, models, api, _

class AccountMove(models.Model):

    _inherit = "account.move"

    document_type_id = fields.Many2one(
        'account.document.type',
        'Document Type')
    document_number = fields.Char(
        string='Document Number')
    is_expo = fields.Boolean(
        string="Is expo",
        compute="_compute_is_expo")

    @api.depends('document_type_id')
    def _compute_is_expo(self):
        for record in self:
            if record.document_type_id.name == 'FACTURAS DE EXPORTACION':
                record.is_expo = True
            else:
                record.is_expo = False
