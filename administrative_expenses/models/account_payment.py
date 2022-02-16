from odoo import models, fields, api, _
from datetime import datetime, date
import logging

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Función para mostrar la fecha de pago en la factura.
    def post(self):
        rec = super(AccountPayment, self).post()
        acc_move_obj = self.env['account.move'].search([('name','=',self.communication)],limit=1)
        if acc_move_obj:
            for record in acc_move_obj:
                if record.invoice_payments_widget:
                    date_str = record.invoice_payments_widget.split()[23].replace('"',"")
                    date_str = date_str.replace(',','')
                    date_dt = datetime.strptime(date_str, '%Y-%m-%d')
                    date_date = date_dt.date()
                    record.register_date = date_date
        return rec
