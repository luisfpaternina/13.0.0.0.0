# -*- coding: utf-8 -*-

import logging
import datetime
import traceback
import time
from collections import Counter
from dateutil.relativedelta import relativedelta
from uuid import uuid4

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import format_date, float_compare
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import profile

_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    customer_number = fields.Integer(string="Número de cliente", related='partner_id.customer_number', store=True, index=True,
                                     depends=['partner_id'])

    @api.model
    def _cron_recurring_create_invoice_batch_afip_validation(self):
        return self._recurring_create_invoice_batch_afip_validation(automatic=True)

    #  @profile('/tmp/prof.profile')
    def _recurring_create_invoice_batch_afip_validation(self, automatic=False):
        start_process_time = time.time()
        _logger.info('Inicio proceso de facturación por lotes')
        auto_commit = self.env.context.get('auto_commit', True)
        cr = self.env.cr
        invoices = self.env['account.move']
        current_date = datetime.date.today()
        imd_res = self.env['ir.model.data']
        template_res = self.env['mail.template']
        afip_ws_max_size_invoices_lot = int(self.env['ir.config_parameter'].get_param('afip_ws_max_size_invoices_lot', 250)) or 250
        if len(self) > 0:
            subscriptions = self
        else:
            domain = [('recurring_next_date', '<=', current_date),
                      ('template_id.payment_mode', '!=', 'manual'),
                      '|', ('in_progress', '=', True), ('to_renew', '=', True)]
            subscriptions = self.search(domain)
        if subscriptions:
            sub_data = subscriptions.read(fields=['id', 'company_id'])
            for company_id in set(data['company_id'][0] for data in sub_data):
                sub_ids = [s['id'] for s in sub_data if s['company_id'][0] == company_id]
                subs = self.with_context(company_id=company_id, force_company=company_id).browse(sub_ids)
                context_invoice = dict(self.env.context, type='out_invoice', company_id=company_id,
                                       force_company=company_id)
                company = self.env['res.company'].browse(company_id)
                client, auth, transport = company._l10n_ar_get_connection("wsfe")._get_client(return_transport=True)

                if automatic and auto_commit:
                    cr.commit()

                try:
                    for subscription in subs:
                        subscription = subscription[0]  # Trick to not prefetch other subscriptions, as the cache is currently invalidated at each iteration
                        # if we reach the end date of the subscription then we close it and avoid to charge it
                        if automatic and subscription.date and subscription.date <= current_date:
                            subscription.set_close()
                            continue
                            # payment + invoice (only by cron)
                        if subscription.template_id.payment_mode in ['validate_send_payment',
                                                                     'success_payment'] and subscription.recurring_total and automatic:
                            try:
                                payment_token = subscription.payment_token_id
                                tx = None
                                if payment_token:
                                    invoice_values = subscription.with_context(lang=subscription.partner_id.lang)._prepare_invoice()
                                    new_invoice = self.env['account.move'].with_context(context_invoice).create(invoice_values)
                                    if subscription.analytic_account_id or subscription.tag_ids:
                                        for line in new_invoice.invoice_line_ids:
                                            if subscription.analytic_account_id:
                                                line.analytic_account_id = subscription.analytic_account_id
                                            if subscription.tag_ids:
                                                line.analytic_tag_ids = subscription.tag_ids
                                    new_invoice.message_post_with_view(
                                        'mail.message_origin_link',
                                        values={'self': new_invoice, 'origin': subscription},
                                        subtype_id=self.env.ref('mail.mt_note').id)
                                    tx = subscription._do_payment(payment_token, new_invoice, two_steps_sec=False)[0]
                                    # commit change as soon as we try the payment so we have a trace somewhere
                                    if auto_commit:
                                        cr.commit()
                                    if tx.renewal_allowed:
                                        msg_body = _('Automatic payment succeeded. Payment reference: <a href=# data-oe-model=payment.transaction data-oe-id=%d>%s</a>; Amount: %s. Invoice <a href=# data-oe-model=account.move data-oe-id=%d>View Invoice</a>.') % (tx.id, tx.reference, tx.amount, new_invoice.id)
                                        subscription.message_post(body=msg_body)
                                        if subscription.template_id.payment_mode == 'validate_send_payment':
                                            subscription.validate_and_send_invoice(new_invoice)
                                        else:
                                            # success_payment
                                            if new_invoice.state != 'posted':
                                                new_invoice.post()
                                        subscription.send_success_mail(tx, new_invoice)
                                        if auto_commit:
                                            cr.commit()
                                    else:
                                        _logger.error('Fail to create recurring invoice for subscription %s',
                                                      subscription.code)
                                        if auto_commit:
                                            cr.rollback()
                                        new_invoice.unlink()
                                if tx is None or not tx.renewal_allowed:
                                    amount = subscription.recurring_total
                                    date_close = (subscription.recurring_next_date +
                                            relativedelta(days=subscription.template_id.auto_close_limit or
                                                               15)
                                    )
                                    close_subscription = current_date >= date_close
                                    email_context = self.env.context.copy()
                                    email_context.update({
                                        'payment_token': subscription.payment_token_id and subscription.payment_token_id.name,
                                        'renewed': False,
                                        'total_amount': amount,
                                        'email_to': subscription.partner_id.email,
                                        'code': subscription.code,
                                        'currency': subscription.pricelist_id.currency_id.name,
                                        'date_end': subscription.date,
                                        'date_close': date_close
                                    })
                                    if close_subscription:
                                        model, template_id = imd_res.get_object_reference('sale_subscription',
                                                                                          'email_payment_close')
                                        template = template_res.browse(template_id)
                                        template.with_context(email_context).send_mail(subscription.id)
                                        _logger.debug(
                                            "Sending Subscription Closure Mail to %s for subscription %s and closing subscription",
                                            subscription.partner_id.email, subscription.id)
                                        msg_body = _(
                                            'Automatic payment failed after multiple attempts. Subscription closed automatically.')
                                        subscription.message_post(body=msg_body)
                                        subscription.set_close()
                                    else:
                                        model, template_id = imd_res.get_object_reference('sale_subscription',
                                                                                          'email_payment_reminder')
                                        msg_body = _('Automatic payment failed. Subscription set to "To Renew".')
                                        if (datetime.date.today() - subscription.recurring_next_date).days in [0, 3, 7,
                                                                                                               14]:
                                            template = template_res.browse(template_id)
                                            template.with_context(email_context).send_mail(subscription.id)
                                            _logger.debug(
                                                "Sending Payment Failure Mail to %s for subscription %s and setting subscription to pending",
                                                subscription.partner_id.email, subscription.id)
                                            msg_body += _(' E-mail sent to customer.')
                                        subscription.message_post(body=msg_body)
                                        subscription.set_to_renew()
                                if auto_commit:
                                    cr.commit()
                            except Exception:
                                if auto_commit:
                                    cr.rollback()
                                # we assume that the payment is run only once a day
                                traceback_message = traceback.format_exc()
                                _logger.error(traceback_message)
                                last_tx = self.env['payment.transaction'].search([('reference', 'like',
                                                                                   'SUBSCRIPTION-%s-%s' % (
                                                                                   subscription.id,
                                                                                   datetime.date.today().strftime(
                                                                                       '%y%m%d')))], limit=1)
                                error_message = "Error during renewal of subscription %s (%s)" % (subscription.code,
                                                                                                  'Payment recorded: %s' % last_tx.reference if last_tx and last_tx.state == 'done' else 'No payment recorded.')
                                _logger.error(error_message)

                        # invoice only
                        elif subscription.template_id.payment_mode in ['draft_invoice', 'manual', 'validate_send']:
                            invoice_values = subscription.with_context(lang=subscription.partner_id.lang)._prepare_invoice()
                            new_invoice = self.env['account.move'].with_context(context_invoice).create(invoice_values)
                            if subscription.analytic_account_id or subscription.tag_ids:
                                for line in new_invoice.invoice_line_ids:
                                    if subscription.analytic_account_id:
                                        line.analytic_account_id = subscription.analytic_account_id
                                    if subscription.tag_ids:
                                        line.analytic_tag_ids = subscription.tag_ids
                            new_invoice.message_post_with_view(
                                'mail.message_origin_link',
                                values={'self': new_invoice, 'origin': subscription},
                                subtype_id=self.env.ref('mail.mt_note').id)
                            # invoices += new_invoice
                            next_date = subscription.recurring_next_date or current_date
                            rule, interval = subscription.recurring_rule_type, subscription.recurring_interval
                            new_date = subscription._get_recurring_next_date(rule, interval, next_date, subscription.recurring_invoice_day)
                            # When `recurring_next_date` is updated by cron or by `Generate Invoice` action button,
                            # write() will skip resetting `recurring_invoice_day` value based on this context value
                            subscription.with_context(skip_update_recurring_invoice_day=True).write({'recurring_next_date': new_date})
                            if subscription.template_id.payment_mode == 'validate_send':
                                invoices += new_invoice
                                _logger.info("Factura %s creada (id: %d): " % (new_invoice.name, new_invoice.id))
                    invoices.post_l10n_ar_batch(client, auth, transport)
                    if automatic and auto_commit:
                        cr.commit()
                except Exception as e:
                    if automatic and auto_commit:
                        cr.rollback()
                        subscription.message_post(
                            body='<p><b>' + _('AFIP Messages') + '</b></p><p><i>%s</i></p>' % (e))
                        _logger.exception('Fail to create recurring invoice for subscription %s, id: %d',
                                          subscription.code, subscription.id)
                    else:
                        raise
        _logger.info("Fin de proceso de facturación por lotes")
        _logger.info("Tardó %s segundos" % (time.time() - start_process_time))
        return invoices

    def _prepare_invoice_line(self, line, fiscal_position, date_start=False, date_stop=False):
        """
        Prepare the dict of values to create the new invoice line.
        We override the method so that it takes the price of the products from the price
        list (in case the product is contained in the list) and if it is not, it will take
        it from the subscription line.
        :param line: sale.order.line record
        :param fiscal_position: sale.fiscal.position record
        :param date_start: start date of the subscription
        :param date_stop: end date of the subscription
        :return: dict to create() the account.invoice.line
        """

        vals = super(SaleSubscription, self)._prepare_invoice_line(line, fiscal_position, date_start, date_stop)
        if 'price_unit' in vals:
            price = self.pricelist_id.item_ids.filtered(  # Search for the price in the price list
                lambda l: l.product_tmpl_id == line.product_id.product_tmpl_id).mapped("fixed_price")
            if price:
                vals['price_unit'] = price[0]
            else:
                vals['price_unit'] = line.price_unit or 0.0
        return vals

