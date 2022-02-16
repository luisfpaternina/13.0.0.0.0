# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, _


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def generate_payment_file(self):
        """
        Cómo armar el archivo TXT que necesitás presentar para cobrar tus débitos automáticos

        Cada archivo TXT está compuesto por 3 partes:
        ENCABEZADO: ocupa la primera línea del documento.
        CUERPO: detalla los débitos a presentar. Cada línea de texto describe un débito, por lo que la cantidad de líneas es variable.
        CIERRE: ocupa la última línea del documento.
        Es importante respetar tanto el orden de las partes como los parámetros de armado definidos para
        cada una. Si se comete algún error en el armado, la presentación no podrá efectuarse.
        ¡Importante! Recordá que deberás armar un archivo por cada marca (Visa y Mastercard) y tipo de tarje-
        ta (crédito y débito). Tené presente que Mastercard solo opera con tarjeta de crédito.
        PARÁMETROS PARA ARMAR EL ENCABEZADO:
        ¡Importante! El _ (guión bajo) indica espacio en blanco.
        Si hacés el TXT con un sistema propio, recordá hacer el salto de línea y retorno de carro al final de cada línea.

        Te mostramos un ejemplo de cómo quedaría armado un encabezado:
        ØDEBLIQC ØØ876543219ØØØØØ    2Ø19Ø5Ø91717Ø         *

        Encabezado:
        A REGISTRO 1 caracter. Completalo con 0 O
        B TARJETA. MARCA Y TIPO 8 caracteres. Completalo según la tarjeta:
            Visa Crédito: DEBLIQC_ Visa Débito: DEBLIQD_
            MasterCard Crédito: DEBLIMC_ DEBLIQC_
        C No ESTABLECIMIENTO PARA DÉBITO AUTOMÁTICO 10 caracteres ØØ87654321
        D CAMPO FIJO 10 caracteres. Completalo con 9ØØØØØ y 4 espacios. 9ØØØØØ____
        E FECHA DE PRESENTACIÓN DEL TXT 8 caracteres. Completalo con AAAAMMDD 2Ø19Ø5Ø9
        F HORA DE ARMADO DEL TXT 4 caracteres. Completalo con HHMM 1717
        G DÉBITOS A LIQUIDAR 1 caracter. Completalo con Ø 0
        H CAMPO FIIJO 2 espacios __
        I CAMPO OPCIONAL 55 caracteres. Usá este campo para agregar info adicional. Si no, completalo con 55 espacios. ___
        J FIN Completalo con * *

        Cuerpo:
        
        PARÁMETROS PARA ARMAR EL CUERPO
        Recordá que necesitás respetar estos parámetros por cada débito automático que quieras presentar.
        Te mostramos un ejemplo de cómo quedaría armado un débito automático a presentar:
        Empresa:
        112376445182Ø6ØØ1 Ø2Ø453352Ø19Ø5Ø9ØØØ5ØØØØØØØØØ17ØØ1ØØØØØØØØØØØ38963E

        A 1 caracter Completlo siempre con 1 1
        B NUMERO DE TARJETA 16 caracteres 12376445182Ø6ØØ1
        C CAMPO FIJO 3 espacios ___
        D No FACTURA O Nro SECUENCIAL  ASCENDENTE 8 caracteres. Identifica a la transacción. Completalo con el no de factura o con un no secuencial ascendente si no emitís comprobante. Ø2Ø45335
        E FECHA DE PRESENTACION DEL TXT 8 caracteres. Completalo con AAAAMMDD 2Ø19Ø5Ø9
        F CÓDIGO DE TRANSACCIÓN 4 caracteres. Completalo con: ØØØ5 si es un débito o 6ØØØ si es una devolución. ØØØ5
        G IMPORTE 15 caracteres. Los últimos 2 son los decimales. ØØØØØØØØØ17ØØ1Ø 15 caracteres Lo definís vos. Deberás mantener el ID asignado a una tarjeta en todas tus presentaciones.
        H ID DEL CLIENTE ØØØØØØØØØØ38963
        I CÓDIGO DE ALTA DE IDENTIFICADOR 1 caracter Si es débito nuevo, completalo con E. Caso contrario, completalo con un espacio.
        J CAMPO FIJO
        K FIN Completalo con * *

        Cierre:
        
        PARÁMETROS PARA ARMAR EL CIERRE
        Te mostramos un ejemplo de cómo quedaría armado un cierre:
        9DEBLIQC ØØ876543219ØØØØØ  2Ø19Ø5Ø91717ØØØØØØ1ØØØØØØØ1ØØØØØ2Ø        *

        A REGISTRO 1 caracter. Completalo con 9 9
        B TARJETA. MARCA Y TIPO 8 caracteres. Completalo según la tarjeta:
            Visa Crédito: DEBLIQC_ Visa Débito: DEBLIQD_
            MasterCard Crédito: DEBLIMC_ DEBLIQC_
        C No ESTABLECIMIENTO PARA  DÉBITO AUTOMÁTICO 10 caracteres ØØ87654321
        D CAMPO FIJO 10 caracteres. Completalo con 9ØØØØØ y 4 espacios. 9ØØØØØ____
        E FECHA DE PRESENTACIÓN DEL TXT 8 caracteres. Completalo con AAAAMMDD 2Ø19Ø5Ø9
        F HORA DE ARMADO DEL TXT 4 caracteres. Completalo con HHMM 1717
        G CANTIDAD TOTAL DE DÉBITOS 7 caracteres ØØØØØØ1
        H IMPORTE DE TODOS
        LOS DÉBITOS 15 caracteres. Los últimos 2 son los decimales. ØØØØØØØ1ØØØØØ2Ø
        I CAMPO OPCIONAL 36 caracteres. Usá este campo para agregar info adicional.
        Si no, completalo con 36 espacios. ___
        J FIN Completalo con * *

        """
        self.ensure_one()
        if self.payment_method_id.code != "dbto_tc_visa_prisma":
            return super(AccountPaymentOrder, self).generate_payment_file()
        transactions_counter = 0
        file_total_amount = 0.0
        lines = []
        # encabezado o header del archivo
        file_header = "{0:<1}".format("Ø") + \
        "{0:<8}".format("DEBLIQC_") + \
        "{0:<10}".format("0091498170") + \
        "{0:<10}".format("900000") + \
        "{0:<8}".format(datetime.now().strftime("%Y%m%d")) + \
        "{0:<4}".format(datetime.now().strftime("%H%M")) + \
        "{0:<1}".format("Ø") + \
        "{0:<2}".format("") + \
        "{0:<55}".format("") + \
        "{0:<1}".format("*")
        lines.append(file_header)
        file_total_amount = 0.0
        for line in self.bank_line_ids:
            transactions_counter += 1
            file_total_amount += line.amount_currency
            # cuerpo o detalle del archivo
            # busco el id de la factura para pasarlo en el archivo
            invoice_id = self.env["account.move"].search([("name", "=", line.communication)], limit=1).id
            file_body = "{0:<1}".format("1") + \
                        "{0:<16}".format(line.partner_bank_id.acc_number) + \
                        "{0:<3}".format("") + \
                        "{0:0>8}".format(invoice_id) + \
                        "{0:<8}".format(datetime.now().strftime("%Y%m%d")) + \
                        "{0:<4}".format("0005") + \
                        "{0:<15}".format(str(line.amount_currency).replace(".", "").zfill(15)) + \
                        "{0:<15}".format(line.partner_id.customer_number) + \
                        "{0:<1}".format("E") + "{0:<28}".format("") + "{0:<1}".format("*")
            # .replace(' ', '').replace('-', '')
            lines.append(file_body)

        # cierre o footer del archivo
        file_footer = "{0:<1}".format("9") + \
            "{0:<8}".format("DEBLIQC_") + \
            "{0:<10}".format("0091498170") + \
            "{0:<10}".format("900000") + \
            "{0:<8}".format(datetime.now().strftime("%Y%m%d")) + \
            "{0:<4}".format(datetime.now().strftime("%H%M")) + \
            "{0:<7}".format(transactions_counter) + \
            "{0:<15}".format(str(file_total_amount).replace(".", "").zfill(15)) + \
            "{0:<36}".format("") + \
            "{0:<1}".format("*")
        lines.append(file_footer)
        return bytes("\n".join(lines), "UTF-8"), "DEBLIQC"

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