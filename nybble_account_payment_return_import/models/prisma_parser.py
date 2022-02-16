from datetime import datetime


class PrismaParser(object):

    # """ Parser for PRISMA files """
    # """ Parse a returned PRISMA file.
    # :param data:
    # :return: account.payment.return records list
    # :raise: ValueError if parsing failed
    #
    # Cómo leés los archivos de tarjetas de crédito (RDEBLIQC y RDEBLIMC):
    #
    # *) detalle del registro cabecera del archivo
    # PARÁMETROS PARA LEER EL ENCABEZADO:
    # ejemplo: Ø RDEBLIQC 9ØØØØØ   ØØ4156Ø5582Ø19Ø42318Ø6
    #
    # A REGISTRO 1 caracter. Completalo con 0
    # B TARJETA. MARCA Y TIPO 8 caracteres. Según la tarjeta verás:
    #     Visa Crédito: RDEBLIQC
    #     MasterCard Crédito: RDEBLIMC
    # C CAMPO FIJO 10 caracteres. Completalo con 9ØØØØØ y 4 espacios. "9ØØØØØ   "
    # D Nro ESTABLECIMIENTO PARA DÉBITO AUTOMÁTICO 10 caracteres ej: ØØ41560558
    # E FECHA DE PRESENTACIÓN DEL TXT 8 caracteres. Completalo con AAAAMMDD 2Ø19Ø423
    # F HORA DE ARMADO DEL TXT 4 caracteres. Completalo con HHMM 18Ø6
    # G CAMPO FIJO 3 espacios ___
    # H CAMPO FIJO 255 caracteres. Es información interna del procesamiento que no necesitás leer. ......
    # J FIN Completalo con * *
    #
    # *) detalle de los registros del cuerpo del archivo
    #
    # PARÁMETROS PARA LEER EL CUERPO:
    # Te mostramos un ejemplo de cómo verías los débitos que vas a cobrar con tarjeta de crédito:
    #     ejemplo: 1Ø675829819ØØØ5 ØØ4156Ø5581234123412341234ØØØØØØØ124Ø419 ØØØØØØØØØ1ØØØØØØ1 ØØØØØØØ33123589EØ457165366Ø25  0  00 456456456456456423Ø41923Ø519Ø1 *
    #
    # A REGISTRO 1 caracter. Completalo con 1 1
    # B Nro DE CÓDIGO DEL BANCO PAGADOR 3 caracteres Ø67
    # C Nro DE SUCURSAL DEL BANCO PAGADOR 3 caracteres 582
    # D Nro DE LOTE 4 caracteres 9819
    # E CÓDIGO DE TRANSACCIÓN 4 caracteres. ØØØ5 indica consumo en $6ØØØ indica devolución ØØØ5
    # F CAMPO FIJO 1 espacio _
    # G Nro ESTABLECIMIENTO PARA DÉBITO AUTOMÁTICO 10 caracteres ØØ4156Ø558
    # H Nro DE TARJETA 16 caracteres 1234123412341234
    # I Nro FACTURA O Nro SECUENCIAL ASCENDENTE 8 caracteres ØØØØØØØ1
    # J FECHA DE PRESENTACIÓN DEL TXT 6 caracteres. Viene como DDMMAA 24Ø419
    # K CAMPO FIJO 6 espacios ______
    # L IMPORTE 15 caracteres. Los últimos 2 son los decimales. ØØØØØØØØØ1ØØØØØ
    # M No DE CUOTA A DEBITAR 2 caracteres Si tu empresa es de seguros, verás el no de cuota (las cuotas con un dígito, tienen un Ø adelante). Caso contrario, verás 2 espacios. 01
    # N CAMPO FIJO 15 espacios _______________
    # Ñ ID DEL CLIENTE Verás el ID que le asignaste a esta tarjeta. Para empresa de seguros, tendrá 13 caracteres + 2 espacios al final.. Si es de otro rubro, tendrá 15 caracteres. ØØØØØØØ33123589
    # O CÓDIGO DE ALTA DE IDENTIFICADOR 1 caracter. Si es débito nuevo, viene con E Caso contrario, viene con 1 espacio. E
    # P CUENTA DE DONDE SE DEBITAN LOS FONDOS 10 caracteres Ø457165366
    # Q CÓDIGO QUE IDENTIFICA EL TIPO DE SEGURO 3 caracteres. Si tu empresa es de seguros, verás este código. Caso contrario, verás 3 espacios. 025
    # R ENDOSO DE LA PÓLIZA 3 caracteres Si tu empresa es de seguros, verás el número de endoso. Caso contrario, verás 3 espacios. ___
    # S CAMPO FIJO 3 espacios ___
    # T ESTADO DEL MOVIMIENTO 1 caracter. Si está rechazado, verás 1 Si está aprobado, verás Ø 0
    # U RECHAZO 1 2 caracteres Verás el código que identifica el tipo de rechazo. Si no está rechazado, verás 2 espacios. __
    # V DESCRIPCIÓN RECHAZO 1 29 caracteres. Verás la descripción del rechazo 1. Si no está rechazado, verás 29 espacios. _____
    # W RECHAZO 2 2 ceros 00 X DESCRIPCIÓN RECHAZO 2 29 espacios ____
    # Y CAMPO FIJO 16 espacios ____
    # Z No DE TARJETA NUEVA 16 caracteres. Tu cliente cambió su tarjeta y no te avisó. Aquí verás el nuevo número. Usalo para tu próxima presentación. 4564564564564564
    # A1 FECHA QUE PRISMA TE DEVUELVE LA RESPUESTA 6 caracteres. Viene como DDMMAA 23Ø419
    # B1 FECHA DE PAGO 6 caracteres. Si no viene detallada, verás 6 espacios. Si viene, tendrá este formato: DDMMAA. 23Ø519
    # C1 No DE CARTERA DE TU CLIENTE 2 caracteres. Los verás con un Ø adelante. 01
    # D1 FIN 1 caracter. Cierra con * *
    #
    # *) detalle del footer del archivo
    # PARÁMETROS PARA LEER EL CIERRE
    # Te mostramos un ejemplo de cómo sería un cierre:
    # ejemplo: 9RDEBLIQC9ØØØØØ ØØ4156Ø5582Ø19Ø42318Ø6ØØØØØØ1ØØØØØØØØØ1ØØØ2Ø *
    #
    # A REGISTRO 1 caracter. Completalo con 9 9
    # B TARJETA. MARCA Y TIPO 8 caracteres. Según la tarjeta verás:
    #     Visa Crédito: RDEBLIQC
    #     MasterCard Crédito: RDEBLIMC RDEBLIQC
    # C CAMPO FIJO 10 caracteres. Completalo con 9ØØØØØ y 4 espacios. 9ØØØØØ____
    # D No ESTABLECIMIENTO PARA DÉBITO AUTOMÁTICO 10 caracteres ØØ41560558
    # E FECHA DE PRESENTACIÓN DEL TXT 8 caracteres. Completalo con AAAAMMDD 2Ø19Ø423
    # F HORA DE ARMADO DEL TXT 4 caracteres. Completalo con HHMM 18Ø6
    # G CANTIDAD TOTAL DE DÉBITOS 7 caracteres ØØØØØØ1
    # H IMPORTE DE TODOS LOS DÉBITOS 15 caracteres. Los últimos 2 son los decimales. ØØØØØØØ1ØØØØØ2Ø
    # J CAMPO FIJO 236 caracteres. Viene con 236 espacios ______
    # K FIN 1 caracter. Cierra con * *
    #
    # """

    def parse(self, data):
        parsed_payment_returns = []
        header_ok = False

        # agregamos validaciones de formato de archivo
        data_str = data.decode('utf-8')
        for line in data_str.split('\n'):

            if line.startswith("0"):  # es linea de encabezado
                # validamos el encabezado del archivo
                assert(line[1:9] == 'RDEBLIQC')
                assert(line[9:19] == "900000    ")
                assert(line[19:29] == "0091498170")
                header_ok = True

            if line.startswith("1"):  # es linea de cuerpo (movimiento)
                customer_number = int(line[94:109])
                amount = float(line[62:75] + "." + line[75:77])
                invoice_id = line[42:50]
                move_state = line[129:130]
                rejection_1_code = line[131:132]
                rejection_1_description = line[132:161]
                rejection_2_code = line[162:163]
                rejection_2_description = line[163:192]
                account_number = line[26:42]
                new_card_number = line[208:224]
                parsed_payment_returns.append({'account_number': account_number,
                                               'name': 'PRISMA',
                                               'date': datetime.strptime(line[224:230], '%d%m%y').date().strftime('%Y-%m-%d'), # fecha de pago B1
                                               'transactions': [
                                                   {
                                                       'amount': amount,
                                                       'concept': line[77:98],
                                                       # 'reason_code': line[70:76],
                                                       # 'reason': "acepted" if move_state == "0" else "rejected " + rejection_1_code + " - " + rejection_1_description,
                                                       'reference': invoice_id,
                                                       'customer_number': customer_number,
                                                   }
                                               ]}),

        return parsed_payment_returns
