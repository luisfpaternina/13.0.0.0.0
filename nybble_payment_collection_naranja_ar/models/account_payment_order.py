# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import _, models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def generate_payment_file(self):

    # FORMATO DEL ARCHIVO DE FACTURACIÓN QUE ENVIAN LAS EMPRESAS DE SERVICIOS A TARJETA NARANJA S.A.
    # Nombre del Archivo : daf-<nro de comercio > - Ejemplo : daf-100175862
    # Contenido: Facturación de las Empresas de Servicios
    # Formato: ASCII – Texto
    # Generado por: Empresas de Servicios
    #

        self.ensure_one()
        if self.payment_method_id.code != "dbto_tarjeta_naranja":
            return super(AccountPaymentOrder, self).generate_payment_file()
        transactions_count_a = 0
        amount_control_sum_a = 0.0
        lines = []

        # Registro Cabecera - Longitud Total: 115 caracteres
        # Orden     Desde   Hasta   Long.   Campo                   Tipo                Descripción                                                                 Formato                                                 Obligatorio         Uso
        # -------------------------------------------------------------------------------------------------------------------------------------------------
        # 1         1       1       1       TIPO DE REGISTRO        Alfanumérico        Indica el tipo de Registro del que se trata                                 X - Valor Predefinido = “C” (registro de cabecera)      Si
        # 2         2       10      9       NRO DE COMERCIO         Numérico            Nro de Comercio asignado por Tarjeta Naranja a la empresa de servicios      999999999                                               SI
        # 3         11      107     97      SIN USO                 Alfanumérico        Sin USO                                                                     Espacios    #    #                                      SI
        # 4         108     115     8       FECHA DE PRESENTACION   Numérico            Fecha de Procesamiento del archivo en la Empresa de servicios               AAAAMMDD - Sin Caracteres especiales                    SI

        file_header = 'C' + "100426625" + "{0:<97}".format("") + datetime.now().strftime('%Y%m%d')
        assert len(file_header) == 115, "El registro cabecera debe tener 115 caracteres"
        lines.append(file_header)

        file_total_amount = 0.0
        for line in self.bank_line_ids:
            transactions_count_a += 1
            file_total_amount += line.amount_currency
            # busco id de factura basado en el nomber de la factura
            invoice_id = self.env["account.move"].search([("name", "=", line.communication)], limit=1).id
            # Registro de Datos - Longitud Total: 115 caracteres
            # Orden     Desde   Hasta   Long.   Campo                       Tipo                Descripción                                                                 Formato                                                Obligatorio         Uso
            # -------------------------------------------------------------------------------------------------------------------------------------------------
            # 1         1       1       1       TIPO DE REGISTRO            Alfanumérico        Indica el tipo de Registro del que se trata                                 X - Valor Predefinido = “D” (registro de detalle)      Si
            # 2         2       17      16      NRO DE TARJETA              Numérico            Nro de Identificación asignado por Tarjeta Naranja al Cliente.              9999999999999999                                       SI
            # 3         18      29      12      IMPORTE                     Numérico            Monto a debitar de la cuenta del cliente
            # 4         30      37      8       FECHA ALTA                  Numérico            Fecha de adhesión del cliente a la empresa de servicios                     AAAAMMDD
            # 5         38      67      30      NRO DE DEBITO               Alfanumérico        Nro de cuenta del cliente en la empresa de servicios                        XXXXXXXXXXXXXXX XXXXXXXXXXXXXXX
            # 6         68      75      8       FECHA DE VENCIMIENTO(**)    Numérico                        AAAAMMDD
            # 7         76      77      2       NRO DE CUOTA                Numérico
            # 8         78      85      8       NRO DE FACTURA (**)         Numérico
            # 9         86      89      4       AÑO DE LA CUOTA (**)        Numérico (***) Alfanumérico
            # 10        90      112     23      DATOS ADICIONALES(***)      Alfanumérico        Sin USO                                                                 Espacios                                                    SI
            # 11        113     115     3       Sin Uso                     Alfanumérico        Sin Uso                                                                 Espacios    #    #    #                                     SI                  Exclusivo TN

            # IMPORTANTE!!! Fecha de adhesión del cliente a la empresa de servicios solo se informa cuando es cliente nuevo

            file_detail_line = "D" + \
                               "{0:<16}".format(line.partner_bank_id.acc_number) + \
                               "{0:0>12}".format(int(round(line.amount_currency, 2) * 100)) + \
                               "00000000" + \
                               "{0:<30}".format(invoice_id) + \
                               "{0:<8}".format(line.date.strftime('%Y%m%d')) + \
                               "{0:0<2}".format("0") + \
                               "{0:0<8}".format("0") + \
                               "{0:0<4}".format("0") + \
                               "{0:<23}".format("") + \
                               "{0:<3}".format("")
            assert len(file_detail_line) == 115, "El registro detalle debe tener 115 caracteres"
            lines.append(file_detail_line)

        # Registro PIE - Longitud Total: 115 caracteres
        # Orden     Desde   Hasta   Long.   Campo                       Tipo                Descripción                                                                 Formato                                                                                     Obligatorio         Uso
        #-------------------------------------------------------------------------------------------------------------------------------------------------
        # 1         1       1       1       TIPO DE REGISTRO            Alfanumérico        Indica el tipo de Registro del que se trata                                 X - Valor Predefinido = “P” (registro pie)                                                   SI
        # 2         2       7       6       CANTIDAD DE REGISTROS       Numérico            Cantidad total de registros                                                 999999                                                                                       SI
        # 3         8       95      88      SIN USO                     Alfanumérico        Sin USO                                                                     Espacios                                                                                     SI
        # 4         96      107     12      MONTO TOTAL                 Numérico            Suma del campo IMPORTE                                                      999999999999 - 10 enteros, 2 decimales. Sin caracteres especiales (punto, coma, etc.)        SI
        # 5         108     115     8       SIN USO                     Alfanumérico        Sin USO                                                                     Espacios                                                                                     SI

        file_footer = "P" + \
                      "{0:0>6}".format(transactions_count_a) + \
                      "{0:<88}".format("") + \
                      "{0:0>12}".format(int(round(file_total_amount, 2) * 100)) + \
                      "{0:<8}".format("")
        assert len(file_header) == 115, "El registro footer debe tener 115 caracteres"
        lines.append(file_footer)

        file_name = "dat-100426625"
        return bytes("\n".join(lines), "UTF-8"), file_name

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