# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import _, models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def generate_payment_file(self):

        # Este es el archivo que la empresa tiene que enviar a Banelco con la información de las
        # facturas que quiere que estén disponibles para que sus clientes puedan pagar. Es del tipo txt.
        # Información operativa
        # Origen: Empresa
        # Destino: Banelco
        # Horarios: Los archivos se transmiten solo los días hábiles antes de las 14:00 hs a través de www.pagomiscuentas.com, ingresando en “Login Empresa” con el usuario y clave asignados.
        # Nombre: FACXXXX.ddmmaa sin ninguna extensión, donde:
        # XXXX: Nro. empresa asignado por Banelco.
        # ddmmaa: Corresponden al día, mes y año de generación del archivo.
        # Longitud de registros: fija de 280 bytes, es decir de 280 caracteres.
        # Código de diseño: 101

        # Conformación de registros
        # Tipo del Registro         Id.Reg.     Descripción global del contenido
        # --------------------------------------------------------------------------------
        # Header                    0           Contiene datos generales del archivo.
        # Detalle                   5           Contiene las facturas informadas por la empresa.
        # Trailer                   9           Contiene los totales del archivo.

        # El archivo está formado por tres partes, un header (que es el primer renglón), el detalle
        # (que está compuesto por la información de las facturas a pagar, hay un renglón por
        # factura) y un trailer (que es el último renglón).

        # Nombre del Registro       Repetición lógica                       Comentario
        # --------------------------------------------------------------------------------
        # Header                    1 por cada archivo                      No puede faltar. Si el archivo no tiene contenido, este registro deberá estar presente.
        # Detalle                   0 ó varios por cada archivo             Si el archivo no tiene contenido este registro no deberá estar presente.
        # Trailer                   1 por cada archivo No puede faltar.     No puede faltar. Si el archivo no tiene contenido, este registro deberá estar presente.

        # Tipos de datos
        # Los campos que conforman los registros se definen con la siguiente nomenclatura: T(nn),
        # donde: “T” Indica el tipo de dato: valores posibles: AN = alfanumérico / N = numérico, y
        # “nn” Indica la longitud.
        # Todos los campos alfanuméricos se alinean a izquierda y se completan con blancos a
        # derecha. Deben estar siempre en letras mayúsculas.
        # Todos los campos numéricos se alinean a derecha y se completan con ceros a izquierda.
        # Si no tiene contenido se completa con ceros.
        
        # Descripción de Registros
        # A continuación se indica cómo construir el archivo, que debe generarse teniendo en
        # cuenta la descripción de cada campo.

        self.ensure_one()
        if self.payment_method_id.code != "pago_mis_cuentas":
            return super(AccountPaymentOrder, self).generate_payment_file()
        transactions_count_a = 0
        amount_control_sum_a = 0.0
        lines = []

        # Elemento / Registro: Header. Descripción de los campos que lo componen.

        # Nro           Atributo                    Tipo de datos       Pos. In.    Pos. Fin.           Descripción - Valores Posibles
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # 1             Codigo Registro             N(01)               001         001                 Código de Registro. Valor fijo: 0. Siempre es 0 e indica que este renglón es el header.
        # 2             Codigo Banelco              N(03)               002         004                 Identificador Banelco. Valor fijo: 400. Siempre es 400 e indica que el ente recaudador es Banelco.
        # 3             Codigo Empresa              N(04)               005         008                 Nro. de empresa asignado por Banelco. Son los cuatro dígitos que figuran en el mail de “Confirmación de aprobación de solicitud” que recibe la empresa.
        # 4             Fecha Archivo               N(08)               009         016                 Fecha de generación del archivo. Formato: AAAAMMDD.
        # 5             Filler                      N(264)              017         280                 Campo para uso futuro. Valor fijo: ceros.

        # armo el encabezado o header del archivo
        file_header = "0" + '400' + '1459' + datetime.today().strftime('%Y%m%d') + '0' * 264
        assert len(file_header) == 280, "El header del archivo debe tener 280 caracteres de longitud. Actualmente tiene %s" % len(file_header)
        lines.append(file_header)
        file_total_amount = 0.0
        for line in self.bank_line_ids:
            transactions_count_a += 1
            file_total_amount += line.amount_currency
            # busco id de factura basado en el nomber de la factura
            invoice_id = self.env["account.move"].search([("name", "=", line.communication)], limit=1).id
            # armo el detalle o cuerpo del archivo
            # Elemento / Registro: Detalle. Descripción de los campos que lo componen.
            # Nro   Atributo                            Tipo                Pos. In.    Pos. Fin.           Descripción - Valores Posibles
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
            # 1     Codigo Registro                     N(01)               001         001                 Código de Registro. Valor fijo: 5. Indica que este renglón forma parte del detalle.
            # 2     Nro.Referencia                      AN(19)              002         020                 Identificación del cliente en la empresa. Se refiere a la identificación que deberá ingresar el cliente para poder pagar, que le sirve a la empresa para saber quien le está pagando. Son los números que componen el “concepto utilizado como ID del cliente” que la empresa completó en el formulario de adhesión.
            # 3     Id.Factura                          AN(20)              021         040                 Identificación de la factura. Se refiere a la identificación particular de la factura que está pagando el cliente. No tiene que ser obligatoriamente el “Nro. de Factura”, sino que puede ser cualquier número que utilice la empresa para individualizar el pago (puede que para un mismo Nro. Referencia, haya varios Id. Factura, si un cliente tiene varias facturas a pagar).
            # 4     Codigo Moneda                       N(01)               041         041                 Código de moneda de los importes informados. Valor fijo: 0 (Pesos). Siempre es 0 e indica que la factura es en pesos.
            # 5     Fecha 1er.Vto.                      N(08)               042         049                 Fecha del 1er vencimiento de la factura Formato: AAAAMMDD
            # 6     Importe 1er.Vto.                    N(11)               050         060                 Importe de la factura para el 1er vencimiento. Formato: 9 enteros, 2 decimales, sin separadores.
            # 7     Fecha 2do.Vto.                      N(08)               061         068                 Fecha del 2do vencimiento de la factura Formato: AAAAMMDD
            # 8     Importe 2do.Vto.                    N(11)               069         079                 Importe de la factura para el 2do vencimiento. Formato: 9 enteros, 2 decimales, sin separadores.
            # 9     Fecha 3er.Vto.                      N(08)               080         087                 Fecha del 3er vencimiento de la factura Formato: AAAAMMDD
            # 10    Importe 3er.Vto.                    N(11)               088         098                 Importe de la factura para el 3er vencimiento. Formato: 9 enteros, 2 decimales, sin separadores.
            # 11    Filler1                             AN(19)              099         117                 Campo para uso futuro. Valor fijo: ceros.
            # 12    Nro.Referencia Ant.                 N(19)               118         136                 Se debe repetir la información del campo “Nro. Referencia”. En caso que se modifique la identificación del cliente, se deberá informar la identificación anterior por única vez, luego se deberá repetir la información del campo Nro. Referencia.
            # 13    Mensaje Ticket                      AN(40)              137         176                 Datos a informar en el ticket de pago. Es el mensaje que se imprimirá en el comprobante de pago que se refiere al concepto abonado por el cliente. Ej: Cuota Noviembre.
            # 14    Mensaje Pantalla                    AN(15)              177         191                 Datos a informar en la pantalla de selección de la factura a pagar. Es el mensaje que verá el cliente en pantalla antes de confirmar el pago. Se refiere al mismo concepto que el campo “Mensaje Ticket”, pero con menos caracteres.
            # 15    Código Barras                       AN(60)              192         251                 Código de barras. Son los números que componen el código de barras de la empresa. Si no posee uno, se debe completar el campo con espacios.
            # 16    Filler2                             N(29)               252         280                 Campo para uso futuro. Valor fijo: ceros.
            file_body_line = '5' + \
                             '{0:<19}'.format(line.partner_id.customer_number) + \
                             '{0:<20}'.format(invoice_id) + \
                             '0' + \
                             '{0:0>8}'.format(line.date.strftime('%Y%m%d')) + \
                             '{0:0>11}'.format(int(round(line.amount_currency, 2) * 100)) + \
                             '{0:0>8}'.format(line.date.strftime('%Y%m%d')) + \
                             '{0:0>11}'.format(int(round(line.amount_currency, 2) * 100)) + \
                             '{0:0>8}'.format("0") + \
                             '{0:0>11}'.format("0") + \
                             '{0:<19}'.format("0") + \
                             '{0:0>19}'.format(line.partner_id.customer_number) + \
                             "{0:<40}".format("DAVITEL - FACTURA: " + line.communication) + \
                             '{0:<15}'.format(line.communication[-16:].replace("-", "").replace(" ", "")) + \
                             '{0:<60}'.format("") + \
                             '{0:0>29}'.format("0")
            assert len(file_body_line) == 280, "Detail Line length is not 280. Actual length: " + str(len(file_body_line))
            lines.append(file_body_line)

        # armo el trailer o footer del archivo
        # Elemento / Registro: Trailer. Descripción de los campos que lo componen.
        # Nro   Atributo                            Tipo de dato        Pos. In.    Pos. Fin.           Descripción – Valores Posibles
        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # 1 Codigo Registro                         N(01)               001         001                 Código de Registro. Valor fijo: 9. Siempre es 9 e indica que este renglón es el trailer.
        # 2 Codigo Banelco                          N(03)               002         004                 Identificador Banelco. Valor fijo: 400. Siempre es 400 e indica que el ente recaudador es Banelco.
        # 3 Codigo Empresa                          N(04)               005         008                 Nro. de empresa asignado por Banelco. Son los cuatro dígitos que figuran en el mail de “Confirmación de aprobación de solicitud” que recibe la empresa.
        # 4 Fecha Archivo                           N(08)               009         016                 Fecha de generación del archivo. Formato: AAAAMMDD
        # 5 Cant.Registros                          N(07)               017         023                 Cantidad de registros de detalle informados. Es la cantidad de renglones que tiene el detalle.
        # 6 Filler1                                 N(07)               024         030                 Campo para uso futuro. Valor fijo: ceros.
        # 7 Total Importe                           N(11)               031         041                 Sumatoria del campo ‘Importe 1er.Vto.’ de los registros de detalle. Formato: 9 enteros, 2 decimales, sin separadores.
        # 8 Filler2                                 N(239)              042         280                 Campo para uso futuro. Valor fijo: ceros.

        file_trailer_line = '9' + \
                            '{0:<3}'.format("400") + \
                            "1459" + \
                            '{0:0>8}'.format(datetime.now().strftime('%Y%m%d')) + \
                            '{0:0>7}'.format(len(lines)) + \
                            '{0:0>7}'.format("0") + \
                            '{0:0>11}'.format(int(round(file_total_amount, 2) * 100)) + \
                            '{0:0>239}'.format("0")
        assert len(file_trailer_line) == 280, "Trailer Line length is not 280, it is: " + str(len(file_trailer_line))
        lines.append(file_trailer_line)
        file_name = "FAC1459." + datetime.now().strftime('%d%m%y')
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