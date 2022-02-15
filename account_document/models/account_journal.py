from odoo import fields, models, api, _

class AccountJournalDocumentType(models.Model):
    _name = "account.journal.document.type"
    _description = "Journal Document Types Mapping"
    _rec_name = 'document_type_id'
    _order = 'journal_id desc, sequence, id'

    document_type_id = fields.Many2one(
        'account.document.type',
        'Document Type')
    journal_id = fields.Many2one('account.journal')
    sequence = fields.Integer(
        'Sequence',
        index=True,
    )
    next_number = fields.Integer()
