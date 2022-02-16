from datetime import datetime


class TarjetaCabalParser(object):

    @staticmethod
    def parse(data):

        parsed_payment_returns = []
        transactions = []
        header_ok = False
        headers_lines_count = 0 # Cantidad de lineas header del archivo procesado

        # contadores para controlar integridad de archivo
        file_payment_count = 0 # Cantidad total de transacciones del Archivo
        file_payment_amount = 0 # Importe total cobrado del archivo

        cabal_merchant_id = 40606882006

        # agregamos validaciones de formato de archivo
        data_str = data.decode('utf-8')
        for line in data_str.split('\r\n'):
            if len(line.strip()) == 0:
                continue
            assert len(line) == 240, 'Linea {} no tiene longitud de 240 caracteres'.format(line)
            file_payment_count += 1
            # customer_number = int(line[0:9])  # nro de cliente
            invoice_id = int(line[0:9])  # cambiamos customer_number por invoice_id
            account_acc = line[9:25]  # nro de tarjeta de la cuenta de la que se cobró
            payment_amount = float(line[25:34] + '.' + line[34:36])  # importe cobrado
            file_payment_amount += payment_amount
            # Código de Rechazos
            # Descripción                                                       Código de Operación        Código Archivode Respuesta
            # Tarjeta Inexistente                                               01                         “I”
            # Inhabilitada para Operar                                          01                         “B”
            # Situación Irregular (mora)                                        01                         “M”
            # Tarjeta Vencida                                                   01                         “V”
            # Sin disponible                                                    01                         “L”
            # Operación Duplicada                                               01                         “D”
            # Stop Debit                                                        01                         “R”
            # Establecimiento Desactivado                                       01                         “N”
            # Tarjeta Inexistente – Bin del Exterior                            01                         “F”
            # Moneda Informada no corresponde a Moneda del Establecimiento      01                         “C"
            # Fecha de Presentación                                             01                         “A”
            # Importe no Válido                                                 01                         “G”
            # Fecha e prestación mayor 35 días                                  01                         “H”
            # No acepta Débitos Automáticos                                     01                         “J”
            # Bloqueo Transitorio                                               01                         “E”
            # Código de operación no numérico                                   01                         "K"
            # Consulte con la identidad                                         01                         “O”
            # Verificar con Sistemas                                            01                         "S"
            assert line[115:116] in [' ', 'I', 'B', 'M', 'V', 'L', 'D', 'R', 'N', 'F', 'C', 'A', 'G', 'H', 'J', 'E', 'K',
                                     'O', 'S'], 'Codigo de Rechazo {} no valido'.format(line[115:116])
            reject_indicator = line[115:116]  # codigo de operacion
            new_credit_card_code = line[116:117]  # nuevo nro de tarjeta - 0: no fue reemplazada - 1: fue reemplazada
            user_info_message = line[118:143]  # Leyenda del débito al Usuario
            # transformo el nombre de la factura
            # 'DAVITEL B0000100001463   '
            # FA-B 00001-00001441
            invoice_name = 'FA-' + user_info_message[-17] + ' ' + user_info_message[-16:-11] + '-' + user_info_message[-11:-3]

            presentation_date = datetime.strptime(line[143:149], '%y%m%d')  # fecha de presentacion
            credit_card_holder_name = line[149:174]  # nombre del titular de la tarjeta
            user_billing_cycle = line[174:176]  # ciclo de facturacion del usuario
            merchant_id = int(line[176:187])  # id del comercio
            assert cabal_merchant_id == merchant_id, "No coincide el id del comercio. Se esperaba {}, se encontro {}".format(cabal_merchant_id, line[176:187])
            currency_code = line[187:188]  # codigo de moneda
            credit_card_due_date = line[188:192]  # fecha de vencimiento de la tarjeta
            new_credit_card_number = line[192:207]  # nuevo nro de tarjeta
            amount_sign = line[208:209]  # signo del importe
            coupon_number = line[209:213]  # nro de cupon
            account_component_number = line[213:215]  # nro de componente de la cuenta - 01: titular - 02 a 09: adicional
            post_code = line[215:223]  # codigo postal
            operation_code = line[223:225]  # codigo de operacion

            payment_return = {'account_number': account_acc,
                                           'name': "Tarjeta Cabal",
                                           'date': datetime.today().strftime('%Y-%m-%d'),
                                           }
            transaction = {
                'amount': payment_amount,
                'reference': invoice_id,
                'date': datetime.today().strftime('%Y-%m-%d'),
                'reason_code': reject_indicator if reject_indicator != ' ' else 'OK'
            }
            payment_return['transactions'] = [transaction]
            parsed_payment_returns.append(payment_return)
        #  parsed_payment_returns[0]['transactions'] = transactions
        return parsed_payment_returns
