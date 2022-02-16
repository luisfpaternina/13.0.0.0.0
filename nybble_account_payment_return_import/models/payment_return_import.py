import logging

from odoo import api, models, _, fields
from odoo.exceptions import UserError
from .bbva_parser import BBVAParser
from .prisma_parser import PrismaParser
from .pagofacil_parser import PagoFacilParser
from .pagomiscuentas_parser import PagoMisCuentasParser
from .tarjeta_naranja_parser import TarjetaNaranjaParser
from .tarjeta_cabal_parser import TarjetaCabalParser

_logger = logging.getLogger(__name__)


class PaymentReturnImport(models.TransientModel):
    _inherit = "payment.return.import"

    # agregamos relacion a metodos de pago para poder selecionarlo y definir como se parsea el archivo segun el
    # metodo de pago
    payment_mode_id = fields.Many2one(
        "account.payment.mode",
        string='Payment Mode',
        required=True,
        domain="[('payment_type', '=', 'inbound')]",
    )

    payment_method_id = fields.Many2one(
        "account.payment.method",
        string='Payment Method',
        related="payment_mode_id.payment_method_id",
        readonly=True,
        )


    @api.model
    def _xml_split_file(self, data_file):
        """BNP France is known to merge xml files"""
        if not data_file.startswith(b"<?xml"):
            return [data_file]
        data_file_elements = []
        all_files = data_file.split(b"<?xml")
        for file in all_files:
            if file:
                data_file_elements.append(b"<?xml" + file)
        return data_file_elements

    @api.model
    def _parse_file(self, data_file):
        data_file_elements = self._xml_split_file(data_file)
        payment_returns = []
        for data_file_element in data_file_elements:
            payment_returns.extend(self._parse_single_document(data_file_element))
        return payment_returns

    @api.model
    def _parse_single_document(self, data_file):
        # Try to parse the file as the following format or fall back for BBVA
        if self.payment_method_id.code == "dbto_cta_bbva":
            parser = BBVAParser()
            try:
                _logger.info(
                    "Try parsing as a BBVA Bank to Customer Debit / Credit Notification.")
                return parser.parse(data_file)
            except ValueError as e:
                _logger.info(
                    "Payment return file is not a BBVA supported file - %s", e,
                    exc_info=True,
                )
                return super(PaymentReturnImport, self)._parse_file(data_file)

        # Try to parse the file as the following format or fall back for PRISMA medios de pago
        elif self.payment_method_id.code == "dbto_tc_visa_prisma":
            parser = PrismaParser()
            try:
                _logger.info("Try parsing as a PRISMA Bank to Customer Debit / Credit Notification.")
                return parser.parse(data_file)
            except ValueError as e:
                _logger.info(
                    "Payment return file is not a PRISMA supported file - %s", e,
                    exc_info=True,
                )
                return super(PaymentReturnImport, self)._parse_file(data_file)

        # Try to parse the file as the following format or fall back for PAGOFACIL medios de pago
        elif self.payment_method_id.code == "pagofacil":
            parser = PagoFacilParser()
            try:
                _logger.info("Try parsing as a PAGOFACIL Bank to Customer Debit / Credit Notification.")
                return parser.parse(data_file)
            except ValueError as e:
                _logger.info(
                    "Payment return file is not a PAGOFACIL supported file - %s", e,
                    exc_info=True,
                )
                return super(PaymentReturnImport, self)._parse_file(data_file)

        # Try to parse the file as the following format or fall back for PAGOMISCUENTAS medios de pago
        elif self.payment_method_id.code == "pago_mis_cuentas":
            parser = PagoMisCuentasParser()
            try:
                _logger.info("Try parsing as a PAGOMISCUENTAS Bank to Customer Debit / Credit Notification.")
                return parser.parse(data_file)
            except ValueError as e:
                _logger.info(
                    "Payment return file is not a PAGOMISCUENTAS " "supported file - %s", e,
                    exc_info=True,
                )
                return super(PaymentReturnImport, self)._parse_file(data_file)

        # Try to parse the file as the following format or fall back for NARANJA  medios de pago
        elif self.payment_method_id.code == "dbto_tarjeta_naranja":
            parser = TarjetaNaranjaParser()
            try:
                _logger.info("Try parsing as a NARANJA Bank to Customer " "Debit Credit Notification. ")
                return parser.parse(data_file)
            except ValueError as e:
                _logger.info(
                    "Payment return file is not a NARANJA " "supported file - %s", e,
                    exc_info=True,
                )
                return super(PaymentReturnImport, self)._parse_file(data_file)

        # Try to parse the file as the following format or fall back for CONFIABLE medios de pago
        elif self.payment_method_id.code == "dbto_tarjeta_cabal":
            parser = TarjetaCabalParser()
            try:
                _logger.info("Try parsing as a CONFIABLE Bank to Customer Debit / Credit Notification.")
                return parser.parse(data_file)
            except ValueError as e:
                _logger.info(
                    "Payment return file is not a CONFIABLE " "supported file - %s", e,
                    exc_info=True,
                )
                return super(PaymentReturnImport, self)._parse_file(data_file)

    @api.model
    def _import_file(self, data_file):
        """ Create bank payment return(s) from file."""
        # The appropriate implementation module returns the required data
        payment_returns = self.env["payment.return"]
        notifications = []
        # payment_return_raw_list = self._parse_all_files(data_file)
        payment_return_raw_list = self._parse_file(data_file)
        # Check raw data:
        self._check_parsed_data(payment_return_raw_list)
        # Import all payment returns:
        for payret_vals in payment_return_raw_list:
            payret_vals = self._complete_payment_return(payret_vals)
            payment_return, new_notifications = self._create_payment_return(payret_vals)
            if payment_return:
                payment_returns += payment_return
            notifications.extend(new_notifications)
        if not payment_returns:
            raise UserError(_("You have already imported this file."))
        return payment_returns, notifications

    @api.model
    def _find_bank_account_id(self, account_number):
        """ Get res.partner.bank ID """
        bank_account_id = None
        bank_account = self.env["res.partner.bank"].search(
            [("acc_number", "=", account_number)], limit=1
        )
        if bank_account:
            bank_account_id = bank_account.id
        return bank_account_id

    @api.model
    def _create_payment_return(self, payret_vals):
        """ Create bank payment return from imported values, filtering out
        already imported transactions, and return data used by the
        reconciliation widget
        """
        pr_model = self.env["payment.return"]
        prl_model = self.env["payment.return.line"]
        # Filter out already imported transactions and create payment return
        ignored_line_ids = []
        filtered_st_lines = []
        for line_vals in payret_vals["transactions"]:
            unique_id = (
                "unique_import_id" in line_vals and line_vals["unique_import_id"]
            )
            if not unique_id or not bool(
                prl_model.sudo().search([("unique_import_id", "=", unique_id)], limit=1)
            ):
                filtered_st_lines.append(line_vals)
                if line_vals.get("customer_number"):
                    line_vals["partner_id"] = self.env["res.partner"].search(
                        [('customer_number', '=', line_vals.get("customer_number"))], limit=1).id
                    line_vals.pop("customer_number")
                # cambio la referencia (invoice_id) por el nombre completo de la factura
                if self.payment_method_id.code in ["dbto_tc_visa_prisma", "pagofacil", "pago_mis_cuentas",
                                                   "dbto_tarjeta_naranja", "dbto_tarjeta_cabal", "dbto_cta_bbva"]:
                    if line_vals.get("reference"):
                        invoice = self.env["account.move"].search(
                            [("id", "=", line_vals.get("reference"))])
                        line_vals["reference"] = invoice.name
                        line_vals["partner_id"] = invoice.partner_id.id
            else:
                ignored_line_ids.append(unique_id)
        payment_return = pr_model.browse()
        if len(filtered_st_lines) > 0:
            # Remove values that won't be used to create records
            payret_vals.pop("transactions", None)
            for line_vals in filtered_st_lines:
                line_vals.pop("account_number", None)
            # Create the payment return
            payret_vals["line_ids"] = [[0, False, line] for line in filtered_st_lines]
            payment_return = pr_model.create(payret_vals)
        # Prepare import feedback
        notifications = []
        num_ignored = len(ignored_line_ids)
        if num_ignored > 0:
            notifications += [
                {
                    "type": "warning",
                    "message": _(
                        "%d transactions had already been imported and " "were ignored."
                    )
                    % num_ignored
                    if num_ignored > 1
                    else _(
                        "1 transaction had already been imported and " "was ignored."
                    ),
                    "details": {
                        "name": _("Already imported items"),
                        "model": "payment.return.line",
                        "ids": prl_model.search(
                            [("unique_import_id", "in", ignored_line_ids)]
                        ).ids,
                    },
                }
            ]
        return payment_return, notifications

    @api.model
    def _complete_payment_return(self, payret_vals):
        """Complete payment return from information passed."""
        # if payret_vals[].get("account_number"):
        account_number = payret_vals.pop("account_number")
        if not payret_vals.get("journal_id"):
            bank_account_id = self._find_bank_account_id(account_number)
            if not bank_account_id and account_number:
                raise UserError(
                    _("Can not find the account number %s.") % account_number
                )
            payret_vals.update(
                {
                    "imported_bank_account_id": bank_account_id,
                    "journal_id": self._get_journal(bank_account_id),
                }
            )
            # By now journal and account_number must be known
            if not payret_vals["journal_id"]:
                raise UserError(_("Can not determine journal for import."))
        else:
            payret_vals["journal_id"] = self.journal_id.id
        for line_vals in payret_vals["transactions"]:
            unique_import_id = line_vals.get("unique_import_id", False)
            if unique_import_id:
                line_vals["unique_import_id"] = (
                    account_number and (account_number + "-") or ""
                ) + unique_import_id
            if not line_vals.get("reason"):
                reason = self.env["payment.return.reason"].name_search(
                    line_vals.pop("reason_code")
                )
                if reason:
                    line_vals["reason_id"] = reason[0][0]
        # else:
        #     payret_vals.update({"journal_id": self.journal_id.id})
        return payret_vals
