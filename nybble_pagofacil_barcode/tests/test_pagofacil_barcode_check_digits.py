import unittest
from odoo.tests import tagged

@tagged('-at_install', 'post_install')
class TestPagofacilBarcodeCheckDigits(unittest.TestCase):

    def test_check_digits(self):
        # selecciono facturas en estado "posted"
        invoice = self.env['account_move'].search([('state', '=', 'posted')] , limit=1)

