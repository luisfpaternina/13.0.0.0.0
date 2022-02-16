from odoo import api, fields, SUPERUSER_ID


def add_sequence_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    sequence_data = {'name': 'Customer Number',
                      'code': 'res.partner.customer.number',
                      'number_next': 1, # setear con el número del máximo cliente importado + 1
                      'company_id': False}
    env['ir.sequence'].create(sequence_data)
