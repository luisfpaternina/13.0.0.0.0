import base64
import json
import logging

from odoo import fields, models, api
from odoo.tools.float_utils import float_round
from datetime import date
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    pagofacil_barcode = fields.Char(compute='_compute_pagofacil_barcode', string='PagoFacil Barcode',
                                    help='Código de barras generado para cobranza mediante PagoFacil')

    # Código de barras
    # A través de los códigos de barras impresos en las facturas, SEPSA realiza la captura de los datos contenidos en el mismo en
    # su sistema. Dichos códigos de barras deberán poseer una cantidad mínima de campos necesarios para su correcto
    # procesamiento. Para ello SEPSA dispone del siguiente diseño standard de registro.

    # Diseño del registro:
    # Campo                     Tipo    Longitud    Desde   Hasta   Descripción
    # ---------------------------------------------------------------------------------------------------------------------
    # Empresa de Servicio       Num.    4           1       4       Identificación de la Empresa.
    # Importe primer venc.      Num.    8           5       12      Formato: 6 enteros 2 decimales.
    # Fecha primer venc.        Num.    5           13      17      Formato: AADDD.
    # Cliente                   Num.    14          18      31      Identificación del cliente.
    # Moneda                    Num.    1           32      32      Valor = "0" pesos.
    # Recargo segundo venc.     Num.    6           33      38      Formato: 4 enteros 2 decimales.
    # Fecha segundo venc.       Num.    2           39      40      Formato: DD.
    # Dígitos verificadores     Num.    2           41      42      Doble verificación.

    # Nota: En caso de que el valor de un campo no posea su longitud máxima, se deberá completar con ceros a la
    # izquierda hasta llegar a la misma.

    # - Empresa de Servicio: Campo por el cual SEPSA identificará a la Empresa. Este valor se compone de los cuatro últimos
    # digitos del número asignado por SEPSA. El mismo será otorgado al iniciar las pruebas técnicas.
    # Ejemplo: número asignado 90060123, valor al código de barras 0123.
    # - Importe primer venc.: Indica el monto de dinero a ser cobrado por la terminal al primer vencimiento.
    # Ejemplo: $ 52,56. = 00005256.
    # - Fecha primer venc.: Fecha límite para el cobro en término del monto antes mencionado. Formato AA: año, DDD: días
    # transcurridos desde el primero de enero inclusive.
    # Ejemplos: 01/01/02 = 02001; 05/07/03 = 03186; 31/12/04 = 04366.
    # - Cliente: Campo por el cual la Empresa identificará a su cliente. El mismo podrá contener datos como: Número de cliente,
    # Recibo, Factura, etc. Puede también subdividir este campo en dos o más campos a efectos de poseer mayor información del
    # pago, como por ejemplo informar el número de cliente más el número de cuota que debe abonar. En caso de que el cliente
    # deba abonar cuotas, se deberá siempre incluir las mismas en este campo.
    # - Moneda: Identifica la moneda de los montos expresados. Valor fijo: 0 pesos.
    # - Recargo segundo venc.: Indica la diferencia de dinero (al primer vencimiento) a ser cobrado por la terminal al segundo
    # vencimiento.
    # Ejemplo: 1°V: $ 174,50.- 2°V: $ 177,80.- = 000330.
    # - Fecha segundo venc.: Indica la diferencia de días entre la fecha del primer vencimiento y la fecha límite de pago al
    # segundo vencimiento. Formato DD.
    # - Dígitos verificadores: Campo por el cual se verifican los dígitos que componen el código de barras. Ver su obtención a
    # continuación.

    @api.depends('l10n_ar_afip_auth_code')
    def _compute_pagofacil_barcode(self):
        """ Method that generates the pagofacil barcode with the electronic invoice information """
        with_qr_code = self.filtered(lambda x: x.l10n_ar_afip_auth_mode in ['CAE', 'CAEA'] and x.l10n_ar_afip_auth_code)
        for rec in with_qr_code:
            self.pagofacil_barcode = self._calculate_pagofacil_barcode_verifier(
                "1312{0:0>8}{1:0>5}{2:0>14}000000000".format(
                    int(float_round(rec.amount_total, 2) * 100),
                    rec.invoice_date_due.strftime('%y') + str((rec.invoice_date_due - date(rec.invoice_date_due.year, 1, 1)).days + 1),
                    rec.id))

    def _calculate_pagofacil_barcode_verifier(self, data):
        """ Method that calculates the pagofacil barcode verifier """
        # Cálculo de los Dígitos verificadores
        # Dado un string numérico, se deberán aplicar los siguientes pasos para la obtención de sus dígitos de verificación.
        # Cálculo del primer dígito verificador:
        # Paso 1: Comenzando por el primer dígito del string numérico, asignarle la secuencia 1, 3, 5, 7, 9; y luego 3, 5, 7, 9 hasta
        # completar la longitud total del mismo.
        # Paso 2: Realizar el producto de cada elemento de la secuencia por el elemento correspondiente del string a verificar.
        # Paso 3: Sumar todos los productos.
        # Paso 4: Dividir el resultado de la suma por 2.
        # Paso 5: Tomar la parte entera del paso 4 y dividirla por 10. El resto de esta división (modulo 10) será el primer dígito
        # verificador.
        # Cálculo del segundo dígito verificador:
        # Paso 6: Agregar el primer dígito verificador obtenido (paso 5) a final de la cadena original, y aplicar nuevamente los pasos 1
        # al 5. El nuevo resultado será el segundo verificador.
        data = list(map(int, list(data)))
        prime_string = [1, 3, 5, 7, 9, 3, 5, 7, 9, 3, 5, 7, 9, 3, 5, 7, 9, 3, 5, 7, 9, 3, 5, 7, 9, 3, 5, 7, 9, 3, 5, 7,
                        9, 3, 5, 7, 9, 3, 5, 7, 9]
        aux_string = []
        # validacion de longitud de datos
        assert len(data) == 40, 'The data must have 40 characters'
        # Paso 2: Realizar el producto de cada elemento de la secuencia por el elemento correspondiente del string a verificar.
        for index, digito in enumerate(data):
            aux_string.append(int(digito) * prime_string[index])
        # Paso 3: Sumar todos los productos.
        suma = sum(aux_string)
        # Paso 4: Dividir el resultado de la suma por 2.
        # Paso 5: Tomar la parte entera del paso 4 y dividirla por 10. El resto de esta división (modulo 10) será el primer dígito
        # verificador.
        primer_dígito_verificador = int((suma / 2)) % 10
        # Paso 6: Agregar el primer dígito verificador obtenido (paso 5) a final de la cadena original, y aplicar nuevamente los pasos 1 al 5. El nuevo resultado será el segundo verificador.
        data.append(primer_dígito_verificador)
        # limpio lista y genero el segundo dígito verificador
        aux_string.clear()
        for index, dígito in enumerate(data):
            aux_string.append(int(dígito) * prime_string[index])
        suma = sum(aux_string)
        segundo_dígito_verificador = int((suma / 2)) % 10
        data.append(segundo_dígito_verificador)
        return "".join(str(e) for e in data)

