from datetime import datetime


class PagoFacilParser(object):

    # Archivo de Transmisión PagoFacil
    # Descripción:
    # A través de los Archivos de Transmisión, SEPSA notifica a las Empresas las transacciones realizadas en toda su red.
    # Estructura del Archivo:
    # La Empresa recibirá un Archivo de Transmisión por día, conteniendo las transacciones realizadas el día o días anteriores (este último caso se da los días Lunes, donde se informa lo cobrado el día Viernes, Sábado y Domingo).

    # Estos archivos están compuestos por Lotes que agrupan hasta 500 transacciones, y cada transacción es informada por tres registros de detalle.

    # Diseño de los registros:

    # Registro Cabecera del Archivo.

    # Campo             Tipo    Longitud    Descripción
    # ---------------------------------------------------------------------------------------------------------------------
    # Record Code       Núm.    1           Código de registro. Valor '1'.
    # Create Date       Núm.    8           Fecha de creación. Formato: AAAAMMDD.
    # Origin Name       Alf.    25          Valor 'PAGO FACIL'.
    # Client Number     Núm.    9           Número de la Empresa.
    # Client Name       Alf.    35          Nombre de la Empresa.
    # Filler            Alf.    50          Completa la longitud fija del registro.

    # Registro Cabecera del Lote. (Sólo uno por lote)

    # Campo             Tipo    Longitud    Descripción
    # ---------------------------------------------------------------------------------------------------------------------
    # Record Code       Núm.    1           Código de registro. Valor '3'.
    # Create Date       Núm.    8           Fecha de creación. Formato: AAAAMMDD.
    # Batch Number      Núm.    6           Número del Lote.
    # Description       Alf.    35          Nombre de la Empresa.
    # Filler            Alf.    78          Completa la longitud fija del registro.

    # Registro de detalle. Información detallada de cada transacción.

    # Campo             Tipo    Longitud    Descripción
    # ---------------------------------------------------------------------------------------------------------------------
    # Record Code       Núm.    1           Código de registro. Valor '5'.
    # Record Sequence   Núm.    5           Número de secuencia de transacción dentro del Lote.
    # Transaction Code  Núm.    2           Código de Transacción.
    # Work Date         Núm.    8           Fecha de Proceso. Formato: AAAAMMDD.
    # Transfer Date     Núm.    8           Fecha de creación. Formato: AAAAMMDD (1).
    # Account Number    Alf.    21          Identificación de la Transacción (campo “Cliente” del registro del código de barras).
    # Currency Code     Alf.    3           Moneda Txs.
    # Amount            Núm.    10          Importe cobrado.
    # Terminal Id.      Alf.    6           Terminal en la cual se efectuó la transacción.
    # Payment Date      Núm.    8           Fecha en que se efectuó la Transacción. Formato: AAAAMMDD.
    # Payment Time      Núm.    4           Hora de la Transacción. Formato: HHMM
    # Term Seq. Number  Núm.    4           Número de secuencia de transacción dentro de la terminal.
    # Filler            Alf.    48          Completa la longitud fija del registro.
    # (1) Es también fecha de transferencia del archivo / fondos (sólo dentro de las 24hs.)

    # Registro de detalle. Código de Barras de la transacción

    # Campo             Tipo    Longitud    Descripción
    # ---------------------------------------------------------------------------------------------------------------------
    # Record Code       Núm.    1           Código de registro. Valor '6'.
    # Bar Code          Núm.    80          Código de Barras de la Transacción.
    # Type Code         Alf.    1           Identifica el origen del código de barras. Valores “S” Site, “O” Online, “ “ Tradicional.
    # Filler            Alf.    46          Completa la longitud fija del registro.

    # Registro de detalle. Detalle de los instrumentos de pago.

    # Campo                 Tipo    Longitud    Descripción
    # ---------------------------------------------------------------------------------------------------------------------
    # Record Code           Núm.    1           Código de registro. Valor '7'.
    # Currency Code         Alf.    3           Moneda del instrumento de pago. Valor ‘PES’: Pesos.
    # Pay Instrument        Alf.    1           Código Instrumento de pago. Valores: ‘E’: Efectivo, ‘C’: Cheque.
    # Code Bar. Pay Inst.   Alf.    80          Código de Barras del instrumento de pago (CMC7 cheques). Ver diseño anexo.
    # Amount                Núm.    15          Importe del instrumento de pago.
    # Filler                Alf.    28          Completa la longitud fija del registro.

    # Registro Cola del Lote. Información total del lote (Sólo uno por lote).

    # Campo                 Tipo    Longitud    Descripción
    # ---------------------------------------------------------------------------------------------------------------------
    # Record Code           Núm.    1           Código de registro. Valor '8'.
    # Create Date           Núm.    8           Fecha de creación del archivo. Formato: AAAAMMDD.
    # Batch Number          Núm.    6           Número del Batch.
    # Batch Payment Count   Núm.    7           Cantidad de transacciones del Lote.
    # Batch Payment Amount  Núm.    12          Importe total cobrado del Lote.
    # Filler                Núm.    38          Valor '0'.
    # Batch Count           Núm.    5           Cantidad de transacciones del Lote.
    # Filler                Alf.    51          Completa la longitud fija del registro.

    # Registro Cola del Archivo. Información total del archivo (Sólo uno por archivo)

    # Campo                 Tipo    Longitud    Descripción
    # Record Code           Núm.    1           Código de registro. Valor '9'.
    # Create Date           Núm.    8           Fecha de creación del archivo. Formato: AAAAMMDD.
    # Total Batches         Núm.    6           Cantidad total de los lotes en el Archivo.
    # File Payment Count    Núm.    7           Cantidad total de transacciones del Archivo.
    # File Payment Amount   Núm.    12          Importe total cobrado del archivo.
    # Filler                Núm.    38          Valor '0'.
    # File Count            Núm.    7           Cantidad total de transacciones del Archivo.
    # Filler                Alf.    49          Completa la longitud fija del registro.
    # Nota: Los campos numéricos se completan con ceros a la izquierda. Los campos alfanuméricos se completan con blancos a la derecha.

    # Denominación del Archivo:
    # Los Archivos poseen la denominación PFddmma.9999. Donde PF hacer referencia a Pago Fácil, ddmma a la Fecha de
    # Proceso del archivo y 9999 los cuatro últimos dígitos correspondientes al número de empresa asignado (campo “empresa de
    # servicios” del código de barras).

    def parse(self, data):
        parsed_payment_returns = []
        transactions = []
        header_ok = False
        headers_lines_count = 0 # Cantidad de lineas header del archivo procesado

        # contadores para controlar integridad de lotes
        batch_payment_count = 0 # Cantidad de transacciones del Lote
        batch_payment_amount = 0 # Importe total cobrado del Lote
        batch_count = 0 # Cantidad de transacciones del Lote

        # contadores para controlar integridad de archivo
        total_batches = 0 # Cantidad total de los lotes en el Archivo
        file_payment_count = 0 # Cantidad total de transacciones del Archivo
        file_payment_amount = 0 # Importe total cobrado del archivo
        file_count = 0 # Cantidad total de transacciones del Archivo


        # Debemnos validar la integridad de la transacción que la determinan que se procesen
        # los registros que comienzan con 5, 6 y 7 de manera consecutiva
        record_integrity = 0

        parsed_payment_returns.append({'name': 'Pago Fácil',
                                       'date': datetime.today().strftime('%Y-%m-%d'),
                                       }),

        # agregamos validaciones de formato de archivo
        data_str = data.decode('utf-8')
        for line in data_str.split('\n'):

            if line.startswith("1"):  # es registro de cabecera de archivo
                # validamos el encabezado del archivo
                headers_lines_count += 1
                record_integrity = 1
                assert line[9:25] == "PAGO FACIL      ", "Se esperaba 'PAGO FACIL      ', se obtuvo: {}".format(line[9:25])
                assert line[34:43] == "090061312", "Se esperaba 9061312, se obtuvo {}".format(line[34:43])
                header_ok = True

            if line.startswith("3"):  # es registro cabecera del lote
                total_batches += 1
                assert record_integrity == 1, "Se está procesando un lote sin un registro de cabecera"
                record_integrity += 1

            if line.startswith("5"):  # es Información detallada de cada transacción
                file_payment_count += 1
                assert record_integrity == 2, "Se está procesando una transacción sin un registro de cabecera"
                record_integrity += 1
                invoice_id = int(line[24:45])
                invoice_currency_code = line[45:48]
                amount_charged = float(line[48:56] + "." + line[56:58])
                file_payment_amount += amount_charged
                batch_payment_amount += amount_charged
                payment_date = datetime.strptime(line[64:71], '%Y%m%d').date()


            if line.startswith("6"): # es Código de Barras de la transacción
                assert record_integrity == 3, "Se está procesando un código de barras sin información detallada de transacción"
                record_integrity += 1
                bar_code = line[1:81]
                bar_code_type = line[81:82]

            if line.startswith("7"): # es Detalle de los instrumentos de pago
                assert record_integrity == 4, "Se está procesando un instrumento de pago sin un código de barras"
                batch_payment_count += 1
                record_integrity = 2 # pongo a 2 (dos) para indicar que debe comenzar a procesar un nuevo registro de información detallada de transacción
                payment_currency_code = line[1:4]
                payment_instrument = line[4:5] # E = efectivo, C = cheque
                payment_instrument_code_bar = line[5:85]
                payment_instrument_amount = float(line[85:98] + "." + line[98:99])
                payment_instrument_date = datetime.strptime(line[16:24], '%Y%m%d')
                transactions.append({
                    'amount': amount_charged,
                    'reference': invoice_id,
                    'date': payment_instrument_date,
                })

            if line.startswith("8"): # es Registro de cierre de lote (indica finalización de lote)
                assert int(line[
                           15:22]) == batch_payment_count, "La cantidad de transacciones del lote no coincide con lo informado en el registro de cierre del lote - Se esperaba: {} y se obtuvo: {}".format(
                    batch_payment_count, int(line[15:22]))
                message = "El importe total cobrado del archivo no coincide con el importe total cobrado del lote" \
                          " informado en el registro de cierre del lote - Se esperaba: {}, se obtuvo: {}"
                assert float(line[22:32] + "." + line[32:34]) == round(batch_payment_amount,
                                                                       2), message.format(
                    float(line[22:32] + "." + line[32:34]), round(batch_payment_amount, 2))
                # pongo a 1 para indicar que debe comenzar a procesar un nuevo registro de cabecera de lote
                record_integrity = 1
                # pongo a 0 el acumulador de montos de lote
                batch_payment_amount = 0
                # pongo a 0 la cantidad de transacciones del lote
                batch_payment_count = 0

        parsed_payment_returns[0]['transactions'] = transactions
        return parsed_payment_returns
