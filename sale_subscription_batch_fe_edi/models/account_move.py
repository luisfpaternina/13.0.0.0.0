import logging
from odoo import fields, models, api, _, exceptions
from datetime import datetime
from odoo.tools.float_utils import float_repr, float_round
from odoo.exceptions import UserError
import re
from dateutil import tz

_logger = logging.getLogger(__name__)

WS_DATE_FORMAT = {'wsfe': '%Y%m%d', 'wsfex': '%Y%m%d', 'wsbfe': '%Y%m%d'}

class AccountMove(models.Model):

    _inherit = "account.move"

    to_reprocess = fields.Boolean(string="Indica si fue rechazado en el proceso batch por un error en otra factura", default=False)

    def post_l10n_ar_batch(self, client, auth, transport):
        """ After validate the invoice we then validate in AFIP. The last thing we do is request the cae because if an
        error occurs after CAE requested, the invoice has been already validated on AFIP """
        ar_invoices = self.filtered(lambda x: x.is_invoice() and x.company_id.country_id == self.env.ref('base.ar'))
        sale_ar_invoices = ar_invoices.filtered(lambda x: x.type in ['out_invoice', 'out_refund'])
        sale_ar_edi_invoices = sale_ar_invoices.filtered(lambda x: x.journal_id.l10n_ar_afip_ws)

        # Verify only Vendor bills (only when verification is configured as 'required')
        (ar_invoices - sale_ar_invoices)._l10n_ar_check_afip_auth_verify_required()

        """ Para validar facturas por lotes el web service AFIP requiere que sean facturas con el mismo tipo de documento y
            con el mismo número de punto de venta (En este caso sería el mismo diario porque para la l10n_ar cada diario tiene un
            punto de venta diferente). """
        journals = list(set([f.journal_id.id for f in sale_ar_edi_invoices]))
        document_types = list(set([f.l10n_latam_document_type_id.id for f in sale_ar_edi_invoices]))
        # separo por diario (punto de venta) y por tipo de documento
        for j in journals:
            for dt in document_types:
                invs = sale_ar_edi_invoices.filtered(lambda x: x.journal_id.id == j and x.l10n_latam_document_type_id.id == dt)
                try:
                    if not dt:
                        raise exceptions.ValidationError(_("En los siguientes id's de facturas no se pudo obtener el tipo de documento AFIP: %s") % ", ".join([str(x.id) for x in invs]))

                    # preparo un lote de facturas para validar en AFIP
                    if invs:
                        document_type = self.env['l10n_latam.document.type'].browse(dt)
                        journal = self.env['account.journal'].browse(j)
                        journal.l10n_ar_sync_next_number_with_afip()
                        _logger.info("Diario %s sincronizado con AFIP" % journal.name)
                        invoice_number = self.env['account.journal'].browse(j)._l10n_ar_get_afip_last_invoice_number(document_type) + 1
                        afip_lot_size = 0
                        general_lot_size = 0
                        start_lot_pointer = 0
                        end_lot_pointer = 0
                        request_data = {}
                        lot_idx = {}
                        invoices = []
                        request_data_det = []
                        ArrayOfFECAEDetRequest = client.get_type('ns0:ArrayOfFECAEDetRequest')

                        # Genero indice de  lote para poder referenciar las
                        # facturas cuando obtenga los datos de respuesta del web service
                        # detalle para state
                        # N = No procesado
                        # S = Procesado Ok
                        # A = Aceptado
                        # R = Rechazado
                        for lot_index, inv in enumerate(invs):
                            invoices.append({'id': lot_index, 'state': 'N', 'invoice_obj': inv})
                        complete = False
                        invoice_number_index = 0
                        lot_index = 0
                        while len(list(filter(lambda invoices: invoices['state'] in ['N', 'R'], invoices))) != 0:
                            _logger.info("lot_index: %d" % lot_index)
                            if invoices[lot_index]['state'] in ['N', 'R']:
                                inv = invoices[lot_index]['invoice_obj']
                                _logger.info("inv.id: %d - state: %s" % (inv.id, invoices[lot_index]['state']))
                            else:
                                lot_index += 1
                                continue
                            # seteamos la tasa de cambio
                            inv.l10n_ar_afip_responsibility_type_id = inv.commercial_partner_id.l10n_ar_afip_responsibility_type_id.id
                            if inv.company_id.currency_id == inv.currency_id:
                                l10n_ar_currency_rate = 1.0
                            else:
                                l10n_ar_currency_rate = inv.currency_id._convert(
                                    1.0, inv.company_id.currency_id, inv.company_id,
                                    inv.invoice_date or fields.Date.today(), round=False)
                            inv.l10n_ar_currency_rate = l10n_ar_currency_rate

                            # armamos en request para el lote

                            partner_id_code = inv._get_partner_code_id(inv.commercial_partner_id)
                            amounts = inv._l10n_ar_get_amounts()
                            due_payment_date = inv._due_payment_date()
                            inv.invoice_date = datetime.now(tz.gettz(self.env['res.users'].browse(self.env.uid).tz))
                            inv._set_afip_service_dates()
                            service_start, service_end = inv._service_dates()

                            related_invoices = inv._get_related_invoice_data()
                            vat_items = inv._get_vat()
                            for item in vat_items:
                                if 'BaseImp' in item and 'Importe' in item:
                                    item['BaseImp'] = float_repr(item['BaseImp'], precision_digits=2)
                                    item['Importe'] = float_repr(item['Importe'], precision_digits=2)
                            vat = partner_id_code and inv.commercial_partner_id.vat and re.sub(r'\D+', '',
                                                                                                inv.commercial_partner_id.vat)

                            tributes = inv._get_tributes()
                            optionals = inv._get_optionals_data()

                            ArrayOfAlicIva = client.get_type('ns0:ArrayOfAlicIva')
                            ArrayOfTributo = client.get_type('ns0:ArrayOfTributo')
                            ArrayOfCbteAsoc = client.get_type('ns0:ArrayOfCbteAsoc')
                            ArrayOfOpcional = client.get_type('ns0:ArrayOfOpcional')
                            request_data_det.append({
                                    'Concepto': int(inv.l10n_ar_afip_concept),
                                    'DocTipo': partner_id_code or 0,
                                    'DocNro': vat and int(vat) or 0,

                                    'CbteDesde': invoice_number + invoice_number_index,
                                    'CbteHasta': invoice_number + invoice_number_index,
                                     # cambiar contador de lote de facturas para que se corresponda con el numero de la factura correcta
                                    'CbteFch': inv.invoice_date.strftime('%Y%m%d'),

                                    'ImpTotal': float_repr(inv.amount_total, precision_digits=2),
                                    'ImpTotConc': float_repr(amounts['vat_untaxed_base_amount'], precision_digits=2),
                                    # Not Taxed VAT
                                    'ImpNeto': float_repr(amounts['vat_taxable_amount'], precision_digits=2),
                                    'ImpOpEx': float_repr(amounts['vat_exempt_base_amount'], precision_digits=2),
                                    'ImpTrib': float_repr(amounts['not_vat_taxes_amount'], precision_digits=2),
                                    'ImpIVA': float_repr(amounts['vat_amount'], precision_digits=2),

                                    # Service dates are only informed when AFIP Concept is (2,3)
                                    'FchServDesde': service_start.strftime(WS_DATE_FORMAT['wsfe']) if service_start else False,
                                    'FchServHasta': service_end.strftime(WS_DATE_FORMAT['wsfe']) if service_end else False,
                                    'FchVtoPago': due_payment_date.strftime(
                                        WS_DATE_FORMAT['wsfe']) if due_payment_date else False,
                                    'MonId': inv.currency_id.l10n_ar_afip_code,
                                    'MonCotiz': float_repr(inv.l10n_ar_currency_rate, precision_digits=6),
                                    'CbtesAsoc': ArrayOfCbteAsoc([related_invoices]) if related_invoices else None,
                                    'Iva': ArrayOfAlicIva(vat_items) if vat_items else None,
                                    'Tributos': ArrayOfTributo(tributes) if tributes else None,
                                    'Opcionales': ArrayOfOpcional(optionals) if optionals else None,
                                    'Compradores': None})
                            invoices[lot_index]['state'] = 'S'
                            invoice_number_index += 1
                            afip_lot_size += 1
                            general_lot_size += 1
                            if afip_lot_size >= 250 or general_lot_size == len(list(filter(lambda invoices: invoices['state'] in ['N', 'R', 'S'], invoices))):
                                # cabecera del request para enviar a AFIP
                                request_data['FeCabReq'] = {'CantReg': afip_lot_size, 'PtoVta': journal.l10n_ar_afip_pos_number,
                                                            'CbteTipo': dt}
                                # detalle del request para enviar a AFIP
                                request_data['FeDetReq'] = ArrayOfFECAEDetRequest(request_data_det)
                                inv._ws_verify_request_data(client, auth, "FECAESolicitar", request_data)
                                response = client.service["FECAESolicitar"](auth, request_data)

                                errors = obs = events = ''
                                # request_data = False
                                return_codes = []

                                to_reprocess = {}

                                if response.FeDetResp:
                                    assert len(request_data_det) == len(response.FeDetResp.FECAEDetResponse)
                                    for idx, req in enumerate(request_data['FeDetReq']['FECAEDetRequest']):
                                        resp = response.FeDetResp.FECAEDetResponse[idx]
                                        assert str(req["CbteFch"]) == str(resp['CbteFch'])
                                        assert str(req["CbteDesde"]) == str(resp['CbteDesde'])
                                        assert str(req["CbteHasta"]) == str(resp['CbteHasta'])
                                        assert str(req["DocTipo"]) == str(resp['DocTipo'])
                                        assert str(req["DocNro"]) == str(resp['DocNro'])
                                        assert str(req["Concepto"]) == str(resp['Concepto'])

                                    # x = start_lot_pointer
                                    x = list(filter(lambda x: x['state'] in ['S'], invoices))[0]['id']
                                    for res in response.FeDetResp.FECAEDetResponse:
                                        x1Inv = invoices[x]['invoice_obj']
                                        values = {}
                                        return_codes = []
                                        _logger.info("Resultado: %s - x1Inv.id: %d - Observaciones: %s" % (res.Resultado, x1Inv.id, res.Observaciones))
                                        if res.Observaciones: # ver resultados de response y de res
                                            obs = ''.join(
                                                ['\n* Code %s: %s' % (ob.Code, ob.Msg) for ob in res.Observaciones.Obs])
                                            return_codes += [str(ob.Code) for ob in res.Observaciones.Obs]
                                        if res.Resultado == 'A':
                                            invoices[x]['state'] = 'A'
                                            try:
                                                super(AccountMove, x1Inv).post_batch()
                                                # x1Inv.l10n_latam_document_number = x1Inv.l10n_latam_sequence_id.next_by_id()
                                                values = {'l10n_ar_afip_auth_mode': 'CAE',
                                                          'l10n_ar_afip_auth_code': res.CAE and str(res.CAE) or "",
                                                          'l10n_ar_afip_auth_code_due': datetime.strptime(res.CAEFchVto, '%Y%m%d').date(),
                                                        'l10n_ar_afip_result': res.Resultado}
                                                x1Inv.write(values)
                                            except Exception as e:
                                                x1Inv.message_post(body='<p><b>' + _('Odoo Validation messages: ') + '</b></p><p><i>%s</i></p>' % (e))
                                        if res.Resultado == 'R' and res.Observaciones:
                                            invoices[x]['state'] = 'X'
                                            _logger.info("Envío RECHAZADO: %d" % x1Inv.id)
                                        if res.Resultado == 'R' and not res.Observaciones:
                                            invoices[x]['state'] = 'R'

                                        if response.Errors:
                                            errors = ''.join(
                                                ['\n* Code %s: %s' % (err.Code, err.Msg) for err in
                                                 response.Errors.Err])
                                            return_codes += [str(err.Code) for err in response.Errors.Err]
                                        if response.Events:
                                            events = ''.join(
                                                ['\n* Code %s: %s' % (evt.Code, evt.Msg) for evt in
                                                 res.Events.Evt])
                                            return_codes += [str(evt.Code) for evt in res.Events.Evt]

                                        return_info = x1Inv._prepare_return_msg("wsfe", errors, obs, events, return_codes)
                                        afip_result = values.get('l10n_ar_afip_result')
                                        xml_response, xml_request = transport.xml_response, transport.xml_request
                                        if afip_result not in ['A', 'O']:
                                            if x1Inv.exists():
                                                # Only save the xml_request/xml_response fields if the invoice exists.
                                                # It is possible that the invoice will rollback as well e.g. when it is automatically created when:
                                                #   * creating credit note with full reconcile option
                                                #   * creating/validating an invoice from subscription/sales
                                                x1Inv.sudo().write({'l10n_ar_afip_xml_request': xml_request,
                                                                  'l10n_ar_afip_xml_response': xml_response})
                                        values.update(l10n_ar_afip_xml_request=xml_request,
                                                      l10n_ar_afip_xml_response=xml_response)
                                        x1Inv.sudo().write(values)
                                        if return_info:
                                            x1Inv.message_post(body='<p><b>' + _('AFIP Messages 000') + '</b></p><p><i>%s</i></p>' % (return_info))
                                            _logger.info('AFIP Messages 000 - %s' % return_info)
                                        x += 1
                                start_lot_pointer = lot_index + 1

                                afip_lot_size = 0
                                general_lot_size = 0
                                request_data = {}
                                request_data_det = []
                            lot_index += 1
                            if lot_index == len(invoices):
                                invoice_number_index = 0
                                lot_index = 0
                                invoice_number = self.env['account.journal'].browse(j)._l10n_ar_get_afip_last_invoice_number(document_type) + 1
                except Exception as e:
                    # TODO: notificar errores en canal de facturación definido o en canal general
                    for inv in invs:
                        inv.message_post(body='<p><b>' + '</b></p><p><i>%s</i></p>' % e)
                        _logger.exception('Fail to validate invoices %s', e)

        return True

    def post_massive_server_action(self):
        # determinamos en que compañía estamos
        company_id = self.env.user.company_id.id
        company = self.env['res.company'].browse(company_id)
        # traemos datos de conexion con AFIP
        client, auth, transport = company._l10n_ar_get_connection("wsfe")._get_client(return_transport=True)
        # procesamos las facturas masivamente
        self.post_l10n_ar_batch(client, auth, transport)
