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
        journal_obj = self.env['account.journal'].search([])
        logging.info("######################")
        logging.info(journal_obj)
        for j in journal_obj:
            if j.is_expo == True:
                logging.info("===============")
                logging.info(j)
                self.journal_id.name = 'Pto Venta 2 - Exportación'
                logging.info("----------------------------------")
