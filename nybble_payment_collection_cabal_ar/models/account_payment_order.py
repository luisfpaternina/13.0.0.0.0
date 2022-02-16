# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import _, models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def generate_payment_file(self):


        self.ensure_one()
        if self.payment_method_id.code != "dbto_tarjeta_cabal":
            return super(AccountPaymentOrder, self).generate_payment_file()
        transactions_count_a = 0
        amount_control_sum_a = 0.0
        lines = []
        numero_de_comercio_cabal = "40606882006"

        # Diseño del Archivo de Presentación de Débito Automáticos
        # Nombre del archivo: COM_001_###########_HHMMSS (########### = 11 dígitos del número de comercio) (HH = Hora) (MM = Mes) (SS = Segundos).
        # Longitud: 240 bytes
        # Formato: Fijo


        # Entorno de homologación
        # Antes de comenzar con la operatoria regular la Empresa deberá enviar un archivo de prueba con el
        # formato correspondiente para que Cabal lo verifique y apruebe si es que no requiriera de modificaciones.
        # Durante esta instancia se podrán intercambiar los archivos vía e-mail dirigiéndose a débitos@cabal.coop.
        # Desde Cabal se le responderá por la misma vía si está correcto o se le indicará lo que deba modificar.
        # El tiempo de implementación se acordará entre las partes.


        file_total_amount = 0.0
        for index, line in enumerate(self.bank_line_ids):
            transactions_count_a += 1
            file_total_amount += line.amount_currency
            # busco id de factura basado en el nomber de la factura
            invoice_id = self.env["account.move"].search([("name", "=", line.communication)], limit=1).id

            # POSICION      LONGITUD    FORMATO         NOMBRE DEL CAMPO                                        VALORES POSIBLES / COMENTARIOS
            # 001-009       9           Numérico        Identificación del socio                                Número con el que la Empresa identifica a su cliente/socio.
            # 010-025       16          Numérico        Número de Tarjeta Cabal                                 IMPORTANTE: actualizar el dato con lo informado en el archivo de respuesta.
            # 026-036       11          Numérico        Importe del Débito                                      Formato: 9 enteros con 2 decimales, sin usar separador decimal.
            # 037-117       81          Alfanumérico    Libre                                                   Completar con espacios.
            # 118-118       1           Alfanumérico    Filler                                                  Completar con espacios.
            # 119-143       25          Alfanumérico    Leyenda que se imprime en el resumen del usuario.
            # 144-149       6           Numérico        Fecha de la Presentación                                Formato: DDMMAA.
            # 150-176       27          Alfanumérico    Libre                                                   Completar con espacios.
            # 177-187       11          Numérico        Número de Comercio Cabal
            # 188-188       1           Alfanumérico    Código de Moneda                                        Informar: ‘P’
            # 189-209       21          Alfanumérico    Libre                                                   Completar con espacios.
            # 210-213       4           Numérico        Número de Cupón                                         No debe repetirse dentro de la misma presentación.
            # 214-223       10          Alfanumérico    Libre                                                   Completar con espacios.
            # 224-225       2           Numérico        Código de Operación                                     ‘01’: Débito al Usuario -’51’: Crédito al Usuario
            # 226-240       15          Alfanumérico    Número de Contribuyente

            # ¿Que es el nro de cupón?

            file_detail_line = "{0:0>9}".format(invoice_id) + \
                               "{0:0>16}".format(line.partner_bank_id.acc_number) + \
                               "{0:0>11}".format(int(round(line.amount_currency, 2) * 100)) + \
                               "{0:<81}".format("") + \
                               "{0:<1}".format("") + \
                               "{0:<25}".format("DAVITEL " + line.communication[-16:].replace("-", "").replace(" ", "")) + \
                               "{0:<6}".format(datetime.now().strftime("%d%m%y")) + \
                               "{0:<27}".format(" ") + \
                               numero_de_comercio_cabal + \
                               "P" + \
                               "{0:<21}".format(" ") + \
                               "{0:0>4}".format(index + 1) + \
                               "{0:<10}".format(" ") + \
                               "{0:0>2}".format("01") + \
                               "{0:0>15}".format(line.partner_id.id)

            assert len(file_detail_line) == 240, "El detalle debe tener 240 caracteres"
            lines.append(file_detail_line)


        file_name = "COM_001_" + numero_de_comercio_cabal + "_" + str(datetime.now().strftime("%H%M%S"))
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