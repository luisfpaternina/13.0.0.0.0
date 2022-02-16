# -*- coding: utf-8 -*-
import datetime

from odoo import _, models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def generate_payment_file(self):
        """Creates the BBVA Debit file.
        creado a partir de documento "Francés net cash"
        Diseño de registro del archivo de Pago directo/Recibos domiciliados
        FNC – v.Cliente 10-2010

        Pago Directo (extensión fichero rec, extensión devolución DVR)
        Formato del fichero Entrada / Salida
        """

        self.ensure_one()
        if self.payment_method_id.code != "dbto_cta_bbva":
            return super(AccountPaymentOrder, self).generate_payment_file()
        transactions_count_a = 0
        amount_control_sum_a = 0.0
        lines = []
        bbva_merchant_id = "28244"

        # RECIBOS. Primer Registro Cabecera. Obligatorio
        #                         Tipo De   A  longitud     observaciones
        # Código de Registro        N   1   4   4           OBL. (Obligatorio) Fijo “4110”.
        header_fmt_field0 = '{0:<4}'
        # Nº. Id empresa            N   5   9   5           OBL. Identificación de la empresa (lo provee el Banco).
        header_fmt_field1 = '{1:<5}'
        # Fecha creación fichero    N   10  17  8           OBL Formato aaaammdd.
        header_fmt_field2 = '{2:<8}'
        # Fecha deseada proceso     N   18  25  8           OBL Formato aaaammdd.
        header_fmt_field3 = '{3:<8}'
        # Banco Emisor              N   26  29  4           OBL Fijo 0017.
        header_fmt_field4 = '{4:<4}'
        # Oficina                   N   30  33  4           OBL Sucursal Cuenta de Cargo.
        header_fmt_field = '{5:<4}'
        # D.C. de la Cuenta         N   34  35  2           OPC Dígito de Control
        header_fmt_field6 = '{6:<2}'
        # Número de Cuenta          N   36  45  10          OBL N°. de la cuenta de cargo
        header_fmt_field7 = '{7:<10}'
        # Cód. de servicio          A   46  55  10          OBL. Código de servicio de la operación (lo provee el Banco).
        header_fmt_field8 = '{8:<10}'
        # Divisa de la cuenta       A   56  58  3           OBL  ARS⇨ Pesos USD ⇨ Dólares
        header_fmt_field9 = '{9:<3}'
        # Indicador devolución      N   59  59  1           OBL Fijo ‘0’
        header_fmt_field10 = '{10:<1}'
        # Nombre del  Fichero.      A/N 60  71  12          OBL Nombre y ext. del fichero actual
        header_fmt_field11 = '{11:12}'
        # Nombre Ordenante          A/N 72  107 36          OBL Nombre Ordenante
        header_fmt_field12 = '{12:<36}'
        # Tipo de cuenta de CBU     N   108 109 2           OBL. Para poder convertir el CCC a CBU.
        header_fmt_field13 = '{13:<2}'
        # Libre                     A   110 250 141         OPC Relleno a blancos.
        header_fmt_field14 = '{14:<141}'

        header_fmt_line = header_fmt_field0 + header_fmt_field1 + header_fmt_field2 + header_fmt_field3 + \
                             header_fmt_field4 + header_fmt_field + header_fmt_field6 + header_fmt_field7 + \
                             header_fmt_field8 + header_fmt_field9 + header_fmt_field10 + header_fmt_field11 + \
                             header_fmt_field12 + header_fmt_field13 + header_fmt_field14
        lines.append(header_fmt_line.format("4110", bbva_merchant_id, datetime.date.today().strftime("%Y%m%d"),
                                        datetime.date.today().strftime("%Y%m%d"),
                                        "0017", "0217", "18", "0100053215", "COBROCUOTA", "ARS", "0", "frances.txt",
                                        "DAVITEL", "20", ""))

        # RECIBOS.Primer registro individual. Obligatorio
        #
        # Código de Registro                                N 1 4  4 OBL. (Obligatorio) Fijo “4210”
        first_record_fmt_field0 = '{0:<4}'
        # Nº. Id empresa                                    N 5 9 5 OBL. Mismo que el reg. De cabecera.
        first_record_fmt_field1 = '{0:<5}'
        # Libre                                             N 10 11 2 Blancos.
        first_record_fmt_field2 = '{0:<2}'
        # Nº.  Id. Beneficiario                             N 12 33 22 OBL. Identificación del beneficiario.  La extensión está fijada por la emisora en Domiciliaciones (la provee el banco).
        first_record_fmt_field3 = '{0:0>22}'
        # CBU                                               N 34 55 22 Cuenta beneficiaria en formato CBU.
        first_record_fmt_field4 = '{0:0<22}'
        # Importe-1                                         N 56 68 13 OBL Importe PARTE ENTERA.
        first_record_fmt_field5 = '{0:0>13}'
        # Importe-2                                         N 69 70 2 OBL Importe PARTE DECIMAL
        first_record_fmt_field6 = '{0:0>2}'
        # Código devolución                                 A 71 76 6 OPC Blancos.  En la devolución se informa el estado.
        first_record_fmt_field7 = '{0:<6}'
        #                                                         CODDE     DESCRIP
        #                                                         000000    CARGADO OK
        #                                                         000001    CUENTA ERRONEA
        #                                                         000002    CUENTA CANCELADA
        #                                                         000003    SALDO INSUF.
        #                                                         000004    STOP DEBIT
        #                                                         000005    BAJA DEL SERVICIO
        #                                                         000006    IMPEDIMENTOS CUEN.
        #                                                         000007    SUCURSAL ERRONEA
        #                                                         000008    REFERENCIA ERRONEA
        #                                                         000009    ADHERENTE INEXISTENTE
        #                                                         000010    OTROS RECHAZOS
        #                                                         000011    FECHA INVALIDA O ERRONEA
        #                                                         000012    MONEDA Y SERVICIO NO COINCIDEN
        #                                                         000013    CUENTA INEXISTENTE
        #                                                         000015    DIA NO LABORABLE
        #                                                         000016    SOPORTE DADO DE BAJA
        #                                                         000017    SERVICIO EN DOLARES NO PERMITIDO
        #                                                         000018    FECHA DE COMPENSACION ERRONEA
        #                                                         000020    RECHAZO DE SOPORTE A SOL CLI
        #                                                         000024    TRANSACCION DUPLICADA
        #                                                         000090    REVERSO NO CORRESPON u OTRO RECHAZO
        #
        # Referencia                                        A 77 98 22 OBL. Libre.
        first_record_fmt_field8 = '{0:0>22}'
        # Fecha de Vencimiento                              N 99 106 8 OBL Formato AAAAMMDD Debe ser mayor o igual que la fecha de proceso.
        first_record_fmt_field9 = '{0:<8}'
        # Libre                                             A 107 108 2 Relleno a blancos.
        first_record_fmt_field10 = '{0:<2}'
        # Número de Factura                                 N 109 123 15 OPC Tanto para CBU de BBVA como de otros bancos se debe informar el n° de CUIL del empleado.
        first_record_fmt_field11 = '{0:<15}'
        # Código de Estado de la dev. de domiciliaciones    A 124 124 1 OBL Relleno a blancos.  En la devolución se informa "C" para devolución parcial y "P" para devolución final.
        first_record_fmt_field12 = '{0:<1}'
        # Descripción de la Devolución                      A 125 164 40 OBL. Relleno a blancos.  En la devolución se informa la descripción del Código de la Devolución.
        first_record_fmt_field13 = '{0:<40}'
        # Libre                                             A 165 250 86 Relleno a blancos.
        first_record_fmt_field14 = '{0:<86}'

        first_fmt_line = first_record_fmt_field0 + first_record_fmt_field1 + first_record_fmt_field2 + \
                         first_record_fmt_field3 + first_record_fmt_field4 + first_record_fmt_field5 + \
                         first_record_fmt_field6 + first_record_fmt_field7 + first_record_fmt_field8 + \
                         first_record_fmt_field9 + first_record_fmt_field10 + first_record_fmt_field11 + \
                         first_record_fmt_field12 + first_record_fmt_field13 + first_record_fmt_field14

        # RECIBOS. Segundo registro individual. Obligatorio
        #
        # Código de Registro N 1 4  4 OBL. (Obligatorio) Fijo “4220”
        second_record_fmt_field0 = '{0:<4}'
        # Nº. Id empresa N 5 9 5 OBL. Mismo que el reg. De cabecera.
        second_record_fmt_field1 = '{0:<5}'
        # Libre 10 11 2 Blancos
        second_record_fmt_field2 = '{0:<2}'
        # Nº.  Id. Beneficiario N 12 33 22 OBL. Mismo que primer reg. individual
        second_record_fmt_field3 = '{0:0>22}'
        # Nombre Beneficiario. A 34 69 36 OBL Nombre del Beneficiario.
        second_record_fmt_field4 = '{0:<36}'
        # Domicilio A/N 70 105 36 OPC Domicilio del Beneficiario
        second_record_fmt_field5 = '{0:<36}'
        # Domicilio (cont.) A/N 106 141 36 OPC Continuación del domicilio.
        second_record_fmt_field6 = '{0:<36}'
        # Libre A 142 250 109 Relleno a blancos.
        second_record_fmt_field7 = '{0:<109}'

        second_fmt_line = second_record_fmt_field0 + second_record_fmt_field1 + second_record_fmt_field2 + \
                             second_record_fmt_field3 + second_record_fmt_field4 + second_record_fmt_field5 + \
                             second_record_fmt_field6 + second_record_fmt_field7

        # RECIBOS. Tercer registro individual. Obligatorio
        #
        # Código de Registro N  1 4  4 OBL. (Obligatorio) Fijo “4230”
        third_record_fmt_field0 = '{0:<4}'
        # Nº. Id empresa N 5 9 5 OBL. Mismo que el reg. De cabecera.
        third_record_fmt_field1 = '{0:<5}'
        # Libre 10 11 2 Blancos
        third_record_fmt_field2 = '{0:<2}'
        # Nº.  Id. Beneficiario N 12 33 22 OBL. Mismo que primer reg. individual
        third_record_fmt_field3 = '{0:0>22}'
        # Localidad A 34 69 36 OPC. Localidad del beneficiario.
        third_record_fmt_field4 = '{0:<36}'
        # Provincia A 70 105 36 OPC. Provincia del beneficiario
        third_record_fmt_field5 = '{0:<36}'
        # Código Postal A/N 106 141 36 OPC. C.P. del beneficiario.
        third_record_fmt_field6 = '{0:<36}'
        # Libre A 142 250 109 Relleno a blancos.
        third_record_fmt_field7 = '{0:<109}'

        third_fmt_line = third_record_fmt_field0 + third_record_fmt_field1 + third_record_fmt_field2 + \
                            third_record_fmt_field3 + third_record_fmt_field4 + third_record_fmt_field5 + \
                            third_record_fmt_field6 + third_record_fmt_field7

        # RECIBOS. Primer  registro de conceptos. Obligatorio.
        #
        # Código de Registro N  1 4  4 OBL. (Obligatorio) Fijo “4240”
        first_record_concepts_fmt_field0 = '{0:<4}'
        # Nº. Id empresa N 5 9 5 OBL. Mismo que el reg. De cabecera.
        first_record_concepts_fmt_field1 = '{0:<5}'
        # Libre N 10 11 2 Blancos
        first_record_concepts_fmt_field2 = '{0:<2}'
        # Nº.  Id. Beneficiario N 12 33 22 OBL. Mismo que primer reg. individual
        first_record_concepts_fmt_field3 = '{0:0>22}'
        # Concepto-1 A/N  34 73 40 OBL. 1er. concepto.  Libre.
        first_record_concepts_fmt_field4 = '{0:<40}'
        # Libre A 74 250 177 Relleno a blancos.
        first_record_concepts_fmt_field5 = '{0:<177}'

        first_fmt_concepts_line = first_record_concepts_fmt_field0 + first_record_concepts_fmt_field1 + \
                                     first_record_concepts_fmt_field2 + first_record_concepts_fmt_field3 + \
                                     first_record_concepts_fmt_field4 + first_record_concepts_fmt_field5

        # RECIBOS. Registro Pie del fichero.
        #
        # Código de Registro N  1 4  4 OBL. (Obligatorio) Fijo “4910”
        footer_record_fmt_field0 = '{0:<4}'
        # Nº. Id empresa N 5 9 5 OBL. Mismo que el reg. De cabecera.
        footer_record_fmt_field1 = '{0:<5}'
        # Importe-parte entera N 10 22 13 OBL  Importe total fichero
        footer_record_fmt_field2 = '{0:0>13}'
        # Importe-parte decimal N 23 24 2 OBL  Parte decimal del importe.
        footer_record_fmt_field3 = '{0:0>2}'
        # Nº. total de operaciones N 25 32 8 OBL  Nº. registros con cód. 4210.
        footer_record_fmt_field4 = '{0:0>8}'
        # Nº. total de registros. N 33 42 10 OBL  Incluyendo cabecera y pie.
        footer_record_fmt_field5 = '{0:0>10}'
        # Libre A 43 250 208 Opc.  Relleno a blancos.
        footer_record_fmt_field6 = '{0:<208}'

        footer_fmt_line = footer_record_fmt_field0 + footer_record_fmt_field1 + footer_record_fmt_field2 + \
                             footer_record_fmt_field3 + footer_record_fmt_field4 + footer_record_fmt_field5 + \
                             footer_record_fmt_field6

        file_total_amount = 0.0
        for line in self.bank_line_ids:
            transactions_count_a += 1
            file_total_amount += line.amount_currency
            # lines.append(first_fmt_line.format("4110", bbva_merchant_id, "", line.partner_id.customer_number,
            #                                    line.partner_bank_id.acc_number, int(line.amount_currency),
            #                                    int(round((line.amount_currency - int(line.amount_currency)), 2) * 100),
            #                                    "",
            #                                    "773743", line.date.strftime("%Y%m%d"), "",
            #                                    line.communication[3:].replace(' ', '').replace('-', ''), "", "", ""))

            invoice_id = self.env['account.move'].search([('name', '=', line.communication)], limit=1).id

            file_first_individual_record = "4210" + \
                                           bbva_merchant_id + \
                                           '{0:<2}'.format("") + \
                                           '{0:0>22}'.format(line.partner_id.customer_number) + \
                                           '{0:0<22}'.format(line.partner_bank_id.acc_number) + \
                                           '{0:0>13}'.format(int(line.amount_currency)) + \
                                           '{0:0>2}'.format(int(round((line.amount_currency - int(line.amount_currency)), 2) * 100)) + \
                                           '{0:<6}'.format("") + \
                                           '{0:0>22}'.format(invoice_id) + \
                                           '{0:<8}'.format(line.date.strftime("%Y%m%d")) + \
                                           '{0:<2}'.format("") + \
                                           '{0:<15}'.format(line.communication[3:].replace(' ', '').replace('-', '')) + \
                                           '{0:<1}'.format("") + \
                                           '{0:<40}'.format("") + \
                                           '{0:<86}'.format("")



            lines.append(file_first_individual_record)


            lines.append(second_record_fmt_field0.format("4220") +
                         second_record_fmt_field1.format(bbva_merchant_id) +
                         second_record_fmt_field2.format("") +
                         second_record_fmt_field3.format(line.partner_id.customer_number) +
                         second_record_fmt_field4.format(line.partner_id.name) +
                         second_record_fmt_field5.format(line.partner_id.address_display[0:35]) +
                         second_record_fmt_field6.format(line.partner_id.address_display[36:71]) +
                         second_record_fmt_field7.format(""))


            # lines.append(third_fmt_line.format("4230", bbva_merchant_id, "", line.partner_id.customer_number, line.partner_id.city,
            #                          line.partner_id.state_id.name, line.partner_id.zip, ""))
            lines.append(third_record_fmt_field0.format("4230") +
                         third_record_fmt_field1.format(bbva_merchant_id) +
                         third_record_fmt_field2.format("") +
                         third_record_fmt_field3.format(line.partner_id.customer_number) +
                         third_record_fmt_field4.format(line.partner_id.city) +
                         third_record_fmt_field5.format(line.partner_id.state_id.name) +
                         third_record_fmt_field6.format(line.partner_id.zip) +
                         third_record_fmt_field7.format(""))

            # lines.append(first_fmt_concepts_line.format("4240", bbva_merchant_id, "", line.partner_id.customer_number, "DEBITOS", ""))
            lines.append(first_record_concepts_fmt_field0.format("4240") +
                         first_record_concepts_fmt_field1.format(bbva_merchant_id) +
                         first_record_concepts_fmt_field2.format("") +
                         first_record_concepts_fmt_field3.format(line.partner_id.customer_number) +
                         first_record_concepts_fmt_field4.format("DEBITOS") +
                         first_record_concepts_fmt_field5.format(""))

        # lines.append(footer_fmt_line.format("4910", bbva_merchant_id, "", "", "", "", "", "", "", "", "", "", ""))
        lines.append(footer_record_fmt_field0.format("4910") +
                     footer_record_fmt_field1.format(bbva_merchant_id) +
                     footer_record_fmt_field2.format(int(file_total_amount)) +
                     footer_record_fmt_field3.format(int(round((file_total_amount - int(file_total_amount)), 2) * 100)) +
                     footer_record_fmt_field4.format(len(self.bank_line_ids)) +
                     footer_record_fmt_field5.format(len(self.bank_line_ids) * 4 + 2) +
                     footer_record_fmt_field6.format(""))


        # retornamos el fichero con nombre "frances.rec"
        return bytes("\n".join(lines), "UTF-8"), "frances.rec"

    # Esta funcion separa la parte entera de la parte decimal de un numero decimal
    def separate_decimal_part(self, number):
        decimal_part = number - int(number)
        return decimal_part

    # Esta funcion separa la parte entera de la parte decimal de un numero decimal
    def separate_integer_part(self, number):
        integer_part = int(number)
        return integer_part

    def generated2uploaded(self):
        """Write 'last debit date' on mandates
        Set mandates from first to recurring
        Set oneoff mandates to expired
        """
        # I call super() BEFORE updating the sequence_type
        # from first to recurring, so that the account move
        # is generated BEFORE, which will allow the split
        # of the account move per sequence_type
        res = super(AccountPaymentOrder, self).generated2uploaded()
        abmo = self.env["account.banking.mandate"]
        for order in self:
            to_expire_mandates = abmo.browse([])
            first_mandates = abmo.browse([])
            all_mandates = abmo.browse([])
            for bline in order.bank_line_ids:
                if bline.mandate_id in all_mandates:
                    continue
                all_mandates += bline.mandate_id
                if bline.mandate_id.type == "oneoff":
                    to_expire_mandates += bline.mandate_id
                elif bline.mandate_id.type == "recurrent":
                    seq_type = bline.mandate_id.recurrent_sequence_type
                    if seq_type == "final":
                        to_expire_mandates += bline.mandate_id
                    elif seq_type == "first":
                        first_mandates += bline.mandate_id
            all_mandates.write({"last_debit_date": order.date_generated})
            to_expire_mandates.write({"state": "expired"})
            first_mandates.write({"recurrent_sequence_type": "recurring"})
            for first_mandate in first_mandates:
                first_mandate.message_post(
                    body=_(
                        "Automatically switched from <b>First</b> to "
                        "<b>Recurring</b> when the debit order "
                        "<a href=# data-oe-model=account.payment.order "
                        "data-oe-id=%d>%s</a> has been marked as uploaded."
                    )
                         % (order.id, order.name)
                )
        return res