from odoo import fields, models, api, _
import logging

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
    journal_expo_id = fields.Many2one(
        'account.journal',
        string="Journal expo")


    @api.depends('document_type_id')
    def _compute_is_expo(self):
        for record in self:
            if record.document_type_id.name == 'FACTURAS DE EXPORTACION':
                record.is_expo = True
            else:
                record.is_expo = False


    @api.onchange('document_type_id','is_expo')
    def _onchange_document(self):
        journal_obj = self.env['account.journal'].search([('name','=', 'Pto Venta 2 - Exportación')],limit=1)
        if journal_obj:
            self.journal_expo_id = journal_obj.id


    @api.onchange('document_type_id')
    def _get_journal(self):
        for record in self:
            if record.is_expo:
                record.journal_id = record.journal_expo_id.id


    @api.onchange(
        'journal_id',
        'document_type_id',
        'invoice_line_ids')
    def _change_account(self):
        for line in self.invoice_line_ids:
            if line.product_id and self.is_expo:
                line.account_id = self.journal_expo_id.default_debit_account_id.id
