from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class AccountJournalDocumentType(models.Model):
    _name = "account.journal.document.type"
    _description = "Journal Document Types Mapping"
    _rec_name = 'document_type_id'
    _order = 'journal_id desc, sequence, id'

    document_type_id = fields.Many2one(
        'account.document.type',
        'Document Type',
        required=True,
        ondelete='cascade',
        auto_join=True,
        index=True,
    )
    sequence_id = fields.Many2one(
        'ir.sequence',
        'Entry Sequence',
        help="This field contains the information related to the numbering of "
        "the documents entries of this document type."
    )
    journal_id = fields.Many2one('account.journal',)
    sequence = fields.Integer(
        'Sequence',
        index=True,
    )
    next_number = fields.Integer()


class AccountJournal(models.Model):
    _inherit = "account.journal"

    journal_document_type_ids = fields.One2many(
        'account.journal.document.type',
        'journal_id',
        'Documents Types',
        auto_join=True,
    )
    use_documents = fields.Boolean(
        'Use Documents?',
    )
    document_sequence_type = fields.Selection(
        # TODO this field could go in argentina localization
        [('own_sequence', 'Own Sequence'),
            ('same_sequence', 'Same Invoice Sequence')],
        string='Document Sequence Type',
        default='own_sequence',
        required=False,
        help="Use own sequence or invoice sequence on Debit and Credit Notes?",
    )
