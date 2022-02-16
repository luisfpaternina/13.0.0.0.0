from datetime import datetime

class BBVAParser(object):
    """Parser for BBVA Bank to Customer Debit Credit Notification."""

    @staticmethod
    def parse_amount(ns, node):
        """Parse element that contains Amount."""
        if node is None:
            return 0.0
        amount = 0.0
        amount_node = node.xpath(
            "./ns:AmtDtls/ns:InstdAmt/ns:Amt", namespaces={"ns": ns}
        )
        if amount_node:
            amount = float(amount_node[0].text)
        return amount

    @staticmethod
    def parse_date(ns, node):
        """Parse element that contains date."""
        date_node = node.xpath("./ns:GrpHdr/ns:CreDtTm", namespaces={"ns": ns})
        return date_node[0].text[:10]

    @staticmethod
    def add_value_from_node(ns, node, xpath_str, obj, key, join_str=None):
        """Add value to object from first or all nodes found with xpath.

        If xpath_str is a list (or iterable), it will be seen as a series
        of search path's in order of preference. The first item that results
        in a found node will be used to set a value in the dictionary."""
        if not isinstance(xpath_str, (list, tuple)):
            xpath_str = [xpath_str]
        for search_str in xpath_str:
            found_node = node.xpath(search_str, namespaces={"ns": ns})
            if found_node:
                if join_str is None:
                    attr_value = found_node[0].text
                else:
                    attr_value = join_str.join([x.text for x in found_node])
                obj[key] = attr_value
                break

    def parse_transaction_details(self, ns, node, transaction):
        """
        Parse transaction details.
        """
        self.add_value_from_node(
            ns, node, "./ns:Refs/ns:EndToEndId", transaction, "reference"
        )
        self.add_value_from_node(
            ns, node, "./ns:RltdDts/ns:IntrBkSttlmDt", transaction, "date"
        )
        self.add_value_from_node(
            ns, node, "./ns:RmtInf/ns:Ustrd", transaction, "concept"
        )
        self.add_value_from_node(
            ns, node, "./ns:RltdPties/ns:Dbtr/ns:Nm", transaction, "partner_name"
        )
        self.add_value_from_node(
            ns,
            node,
            "./ns:RltdPties/ns:DbtrAcct/ns:Id/ns:IBAN",
            transaction,
            "account_number",
        )
        self.add_value_from_node(
            ns, node, "./ns:RtrInf/ns:Rsn/ns:Cd", transaction, "reason_code"
        )
        self.add_value_from_node(
            ns,
            node,
            "./ns:RtrInf/ns:AddtlInf",
            transaction,
            "reason_additional_information",
        )

    def parse_transactions(self, ns, node, transactions):
        """
        Parse transactions (entry) node.
        """
        details_nodes = node.xpath("./ns:NtryDtls/ns:TxDtls", namespaces={"ns": ns})
        for details_node in details_nodes:
            return_info = details_node.xpath("./ns:RtrInf", namespaces={"ns": ns})
            if not return_info:
                continue
            transaction = {}
            transaction["amount"] = self.parse_amount(ns, details_node)
            self.parse_transaction_details(ns, details_node, transaction)
            transaction["raw_import_data"] = etree.tostring(details_node)
            transactions.append(transaction)
        return transactions

    def parse_payment_returns(self, ns, node):
        """
        Parse entry node.
        """
        return_date = self.parse_date(ns, node)
        payment_returns = []
        notification_nodes = node.xpath("./ns:Ntfctn", namespaces={"ns": ns})
        for notification_node in notification_nodes:
            entry_nodes = notification_node.xpath("./ns:Ntry", namespaces={"ns": ns})
            for i, entry_node in enumerate(entry_nodes):
                payment_return = {}
                self.add_value_from_node(
                    ns, notification_node, "./ns:Id", payment_return, "name"
                )
                payment_return["date"] = return_date
                self.add_value_from_node(
                    ns,
                    notification_node,
                    "./ns:Acct/ns:Id/ns:IBAN",
                    payment_return,
                    "account_number",
                )
                payment_return["transactions"] = []
                transactions = []
                self.parse_transactions(ns, entry_node, transactions)
                payment_return["transactions"].extend(transactions)
                subno = 0
                for transaction in payment_return["transactions"]:
                    subno += 1
                    transaction[
                        "unique_import_id"
                    ] = "{return_name}{entry_subno}{transaction_subno}".format(
                        return_name=payment_return["name"],
                        entry_subno=i,
                        transaction_subno=subno,
                    )
                payment_returns.append(payment_return)
        return payment_returns

    def check_version(self, ns, root):
        """
        Check whether the validity of the camt.054.001.02 file.
        :raise: ValueError if not valid
        """
        # Check whether it's a CAMT Bank to Customer Debit Credit Notification
        if not RE_CAMT.search(ns):
            raise ValueError("no camt: " + ns)
        # Check the camt version
        if not RE_CAMT_VERSION.search(ns):
            raise ValueError("no camt.054.001.02: " + ns)
        # Check GrpHdr element
        root_0_0 = root[0][0].tag[len(ns) + 2 :]  # strip namespace
        if root_0_0 != "GrpHdr":
            raise ValueError("expected GrpHdr, got: " + root_0_0)

    def parse(self, data):
        """
        Parse a retuned BBVA file.
        :param data: flat text file content to parse
        :return: account.payment.return records list
        :raise: ValueError if parsing failed
        """

        # contadores para controlar integridad de lotes
        batch_payment_count = 0 # Cantidad de transacciones del Lote
        batch_payment_amount = 0 # Importe total cobrado del Lote
        batch_count = 0 # Cantidad de transacciones del Lote

        # contadores para controlar integridad de archivo
        total_batches = 0 # Cantidad total de los lotes en el Archivo
        file_payment_count = 0 # Cantidad total de transacciones del Archivo
        file_payment_amount = 0 # Importe total cobrado del archivo
        file_count = 0 # Cantidad total de transacciones del Archivo

        parsed_payment_returns = []
        bbva_mercchant_id = "28244"
        bbva_issuing_bank_id = "0017"

        # agregamos validaciones de formato de archivo
        # validaciones de integridad de archivo
        # leemos primera linea y validamos el código de registro y el identificador de la empresa
        header_records_counter, first_record_counter, second_record_counter, third_record_counter, \
            first_concepts_record_counter, footer_records_counter = 0, 0, 0, 0, 0, 0

        data_str = data.decode()
        for line in data_str.split("\n"):
            if line.startswith("4110"):
                header_records_counter += 1
                assert line[4:9] == bbva_mercchant_id, "El identificador de la empresa no coincide. Se esperaba: {} y se encontró: {}".format(bbva_mercchant_id, line[4:9])
                assert line[25:29] == bbva_issuing_bank_id, "El identificador del banco no coincide. Se esperaba: {} y se encontró: {}".format(bbva_issuing_bank_id, line[25:29])

            #
            if line.startswith("4210"):
                first_record_counter += 1
                """ Each module adding a file support must extends this method. It
                processes the file if it can, returns super otherwise, resulting in a
                chain of responsability.
                This method parses the given file and returns the data required by
                the bank payment return import process, as specified below.
                - bank payment returns data: list of dict containing (optional
                                        items marked by o) :
                    -o account number: string (e.g: 'BE1234567890')
                        The number of the bank account which the payment return
                        belongs to
                    - 'name': string (e.g: '000000123')
                    - 'date': date (e.g: 2013-06-26)
                    - 'transactions': list of dict containing :
                        - 'amount': float
                        - 'unique_import_id': string
                        -o 'concept': string
                        -o 'reason_code': string
                        -o 'reason': string
                        -o 'partner_name': string
                        -o 'reference': string
                """
                assert line[4:9] == bbva_mercchant_id, "El identificador de la empresa no coincide. Se esperaba: {} y se encontró: {}".format(bbva_mercchant_id, line[4:9])
                reason_code = int(line[70:76].strip())
                invoice_id = int(line[76:98])
                charged_amount = float(line[56:68] + '.' + line[69:70])
                file_payment_count += 1
                file_payment_amount += charged_amount
                parsed_payment_returns.append({'account_number': line[33:55],
                                               'name': "BBVA",
                                               'date': datetime.today().strftime('%Y-%m-%d'),
                                               'transactions': [
                                                   {
                                                       'amount': charged_amount,
                                                       'unique_import_id': line[77:98],
                                                       'concept': line[77:98],
                                                       'reason_code': '{0:0>6}'.format(reason_code),
                                                       'partner_name': line[12:33],
                                                       'reference': invoice_id,
                                                   }
                                               ]}),
            if line.startswith("4220"):
                second_record_counter += 1
            if line.startswith("4230"):
                third_record_counter += 1
            if line.startswith("4240"):
                first_concepts_record_counter += 1
            if line.startswith("4910"):
                footer_records_counter += 1
                assert file_payment_count == int(
                    line[25:32]), "El número de operaciones no coincide. Se esperaba: {} y se encontró: {}".format(
                    file_payment_count, line[25:32])
        return parsed_payment_returns

