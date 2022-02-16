from datetime import datetime


class TarjetaNaranjaParser(object):

    def parse(self, data):

        parsed_payment_returns = []
        transactions = []
        header_ok = False
        headers_lines_count = 0 # Cantidad de lineas header del archivo procesado

        # contadores para controlar integridad de archivo
        file_payment_count = 0 # Cantidad total de transacciones del Archivo
        file_payment_amount = 0 # Importe total cobrado del archivo

        parsed_payment_returns.append({'name': 'Tarjeta Naranja',
                                       'date': datetime.today().strftime('%Y-%m-%d'),
                                       }),

        # agregamos validaciones de formato de archivo
        data_str = data.decode('utf-8')
        for line in data_str.split('\n'):

            if line.startswith("C"):  # es registro de cabecera de archivo
                assert len(line.strip()) == 115, 'Linea {} no tiene longitud de 115 caracteres'.format(line)
                # validamos el encabezado del archivo
                headers_lines_count += 1
                assert line[1:10] == "800061964", "Se esperaba '800061964', se obtuvo: {}".format(line[1:10])
                file_generated_date = datetime.strptime(line[107:115], '%Y%m%d')
                header_ok = True

            if line.startswith("D"):  # es registro de detalle de archivo
                assert len(line.strip()) == 115, 'Linea {} no tiene longitud de 115 caracteres'.format(line)
                assert header_ok is True, "Se está procesando un lote sin un registro de cabecera"
                file_payment_count += 1
                account_acc = line[1:17]  # nro de tarjeta de la cuenta de la que se cobró
                payment_amount = float(line[17:27] + '.' + line[27:29])  # importe cobrado
                file_payment_amount += payment_amount
                customer_number = int(line[37:67])  # nro de cliente
                invoice_date_due = datetime.strptime(line[67:75], '%Y%m%d')  # fecha de vencimiento de la factura
                invoice_id = int(line[77:85])  # nro de factura
                state_code = line[112:115]  # codigo de movimiento

                transactions.append({
                    'account_number': account_acc,
                    'amount': payment_amount,
                    'reference': invoice_id,
                    'date': invoice_date_due.strftime('%Y-%m-%d'),
                })

            if line.startswith("P"):  # es Registro de cierre de lote (indica finalización de lote)
                assert len(line.strip()) == 115, 'Se esperaba una linea de 115 caracteres. Se encontró: {}'.format(
                    len(line.strip()))
                assert file_payment_count == int(line[1:7]), "Se esperaba {} transacciones, se obtuvo: {}".format(
                    file_payment_count, line[1:7])
                assert round(file_payment_amount, 2) == float(
                    line[96:105] + '.' + line[105:107]), "Se esperaba {} como importe total del archivo, se obtuvo: {}".format(
                    file_payment_amount, line[96:105] + '.' + line[105:107])
                assert headers_lines_count == 1, "Se esperaba 1 cabecera, se obtuvo: {}".format(headers_lines_count)

        parsed_payment_returns[0]['transactions'] = transactions
        return parsed_payment_returns
