from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.onchange("journal_id")
    def _onchange_journal(self):
        #  Sobreescribimos el onchange de journal_id para corregir el método del modulo account_payment_fix en
        #  https://github.com/ingadhoc/account-payment/blob/6c789135653fdb5e18a7b07572d8dd973d118926/account_payment_fix/models/account_payment.py#L165
        #  que devuelve None si no está seteado el journal_id y debería devolver un dict vacío para que no falle el método en modulo
        #  account_payment_order.
        #  Deberíamos generar un pull request sobre el módulo account_payment_fix (Adhoc) y corregir el bug.
        if self.journal_id:
            self.currency_id = (
                self.journal_id.currency_id or self.company_id.currency_id)
            # Set default payment method
            # (we consider the first to be the default one)
            payment_methods = (
                self.payment_type == 'inbound' and
                self.journal_id.inbound_payment_method_ids or
                self.journal_id.outbound_payment_method_ids)
            # si es una transferencia y no hay payment method de origen,
            # forzamos manual
            if not payment_methods and self.payment_type == 'transfer':
                payment_methods = self.env.ref(
                    'account.account_payment_method_manual_out')
            self.payment_method_id = (
                payment_methods and payment_methods[0] or False)
            # si se eligió de origen el mismo diario de destino, lo resetiamos
            if self.journal_id == self.destination_journal_id:
                self.destination_journal_id = False
        #     # Set payment method domain
        #     # (restrict to methods enabled for the journal and to selected
        #     # payment type)
        #     payment_type = self.payment_type in (
        #         'outbound', 'transfer') and 'outbound' or 'inbound'
        #     return {
        #         'domain': {
        #             'payment_method_id': [
        #                 ('payment_type', '=', payment_type),
        #                 ('id', 'in', payment_methods.ids)]}}
        return {}
