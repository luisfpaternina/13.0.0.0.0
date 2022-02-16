from datetime import datetime


class PagoMisCuentasParser(object):

    @staticmethod
    def parse(data):

        # Introducción
        # Este es el archivo que la empresa tiene que descargar diariamente con la información de las
        # cobranzas a acreditar. En caso de que no haya cobranzas el archivo se generará igual pero solo
        # con Header y Trailer. Es del tipo txt.
        # Información general
        # Origen: Banelco
        # Destino: Empresa
        # Horarios: Los archivos se dejan a disposición de la empresa solo los días hábiles, entre
        # las 19:30 y las 22 hs. Se descargan de www.pagomiscuentas.com, ingresando en “Login
        # Empresa” con el usuario y clave asignados.
        # Nombre: COBXXXX.DDMMAA sin ninguna extensión, donde:
        # XXXX: Es el número de empresa otorgado por Banelco
        # DDMMAA: Corresponde a la fecha de acreditación de fondos a la empresa
        # Longitud de registro: Fija de 100 bytes, es decir de 100 caracteres.

        # Conformación de registros
        # Tipo del Registro         Id.Reg.     Descripción global del contenido
        # Header                    0           Contiene datos generales del archivo.
        # Detalle                   5           Contiene las cobranzas que se le acreditarán a la empresa.
        # Trailer                   9           Contiene los totales del archivo.

        # El archivo está formado por tres partes, un header (que es el primer renglón), el detalle (que
        # está compuesto por la información de las cobranzas que se le acreditarán a la empresa, un
        # reglón por cada una) y un trailer (que es el último renglón)

        parsed_payment_returns = []
        transactions = []
        header_ok = False
        headers_lines_count = 0  # Cantidad de lineas header del archivo procesado

        # contadores para controlar integridad de archivo
        file_payment_count = 0  # Cantidad total de transacciones del Archivo
        file_payment_amount = 0  # Importe total cobrado del archivo

        parsed_payment_returns.append({'name': 'Pago Mis Cuentas',
                                       'date': datetime.today().strftime('%Y-%m-%d'),
                                       }),

        # agregamos validaciones de formato de archivo
        data_str = data.decode('utf-8')
        for line in data_str.split('\n'):

            if line.startswith("0"):  # es registro de cabecera de archivo
                assert len(line.strip()) == 100, 'Se esperaba una linea de 100 caracteres. Se encontró: {}'.format(
                    len(line.strip()))
                # validamos el encabezado del archivo
                headers_lines_count += 1
                assert line[1:4] == "400", "Se esperaba '400', se obtuvo: {}".format(line[1:4])
                assert line[4:8] == "1459", "Se esperaba 1459, se obtuvo: {}".format(line[4:8])
                file_generated_date = datetime.strptime(line[8:16], '%Y%m%d')
                header_ok = True

            if line.startswith("5"):  # es registro de detalle de archivo
                assert len(line.strip()) == 100, 'Se esperaba una linea de 100 caracteres. Se encontró: {}'.format(
                    len(line.strip()))
                file_payment_count += 1
                assert header_ok is True, "Se está procesando un lote sin un registro de cabecera"
                customer_number = int(line[1:19])  # Nro de referencia
                invoice_id = int(line[19:40])  # id de factura
                invoice_due_date = datetime.strptime(line[40:48], '%Y%m%d')  # fecha de vencimiento
                payment_date = datetime.strptime(line[49:57], '%Y%m%d')  # fecha en que se cobró la factura
                payment_amount = float(line[57:66] + '.' + line[66:68])  # importe cobrado
                file_payment_amount += payment_amount
                move_code = line[69:70]  # 1: pago sin factura, 2: pago con factura
                acreditation_date = datetime.strptime(line[69:77], '%Y%m%d')  # fecha de acreditación de fondos a la empresa
                payment_channel = line[77:79]  # PC: PagoMisCuentas, HB: Home BAnking, S1: ATM
                control_number = int(line[79:83])

                transactions.append({
                    'amount': payment_amount,
                    'reference': invoice_id,
                    'date': payment_date.strftime('%Y-%m-%d'),
                })

            if line.startswith("9"):  # es Registro de cierre de lote (indica finalización de lote)
                assert len(line.strip()) == 100, 'Se esperaba una linea de 100 caracteres. Se encontró: {}'.format(
                    len(line.strip()))
                assert line[1:4] == "400", "Se esperaba '400', se obtuvo: {}".format(line[1:4])
                assert line[4:8] == "1459", "Se esperaba 1459, se obtuvo: {}".format(line[4:8])
                file_generated_date = datetime.strptime(line[8:16], '%Y%m%d')  # fecha de generación del archivo
                assert file_payment_count == int(line[16:23]), "Se esperaba {} transacciones, se obtuvo: {}".format(
                    file_payment_count, line[16:23])
                assert round(file_payment_amount, 2) == float(
                    line[30:39] + '.' + line[39:41]), "Se esperaba {} como importe total del archivo, se obtuvo: {}".format(
                    file_payment_amount, line[30:39] + '.' + line[39:41])
                assert headers_lines_count == 1, "Se esperaba 1 cabecera, se obtuvo: {}".format(headers_lines_count)

        parsed_payment_returns[0]['transactions'] = transactions
        return parsed_payment_returns
