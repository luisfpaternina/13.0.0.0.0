# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from calendar import monthrange
_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = 'project.task'

    service_start_up = fields.Datetime(string="Operativo desde",
                                       help="Fecha y hora en que el servicio quedó operativo para el cliente")
    origin_sale_order_state = fields.Selection(
        [('draft', 'Borrador'), ('sent', 'Enviado'), ('sale', 'Venta'), ('done', 'Terminado'), ('cancel', 'Cancelado')],
        string="Estado de la orden de venta", related="sale_line_id.order_id.state")

    @api.onchange('service_start_up')
    def set_service_startup(self):
        """
        Cuando seteo la fecha de inicio del servicio debo calcular los días
        efectivos de servicio brindado al clientes para poder facturar correctamente
        y hacer el descuento correspondiente
        """
        if self.sale_line_id:
            _logger.info(self.sale_line_id)
            #
            enjoyed_service_days_product_id = self.env['ir.config_parameter'].sudo().get_param(
                'nybble_startup_service_date.enjoyed_service_days_product_id')
            if not enjoyed_service_days_product_id:
                raise ValidationError(
                    "No está seteado el producto usado para los descuentos por días no gozados. Por favor setearlo en Ventas -> Ajustes y volver a intentarlo.")
            subscription_total_mount = 0
            for ol in self.sale_order_id.order_line:
                if ol.product_id.recurring_invoice:
                    _logger.info(ol.price_unit)
                    subscription_total_mount += ol.price_unit
                # valido que no se haya generado ya un descuento por días no gozados
                if ol.product_id.id == int(enjoyed_service_days_product_id):
                    raise ValidationError('Ya se ha generado un descuento por días no gozados para este servicio.')
            # En la primer facturación de alta a un cliente como se ve en la imagen se incluirá un producto llamado cargo
            # por días proporcionales. Este producto debe poder ser configurado desde el modulo suscripciones y su
            # función será que el valor de dicho producto será por la cantidad de días que queden en el mes después de la
            # fecha de instalación (fecha en la que se pasa la orden de Field service a Hecho) para dicho calculo deberá
            # tomar la totalidad de los valores de suscripciones que posea la orden de venta dividirlo por el total
            # de días del mes y multiplicarlos por los días que quedan de dicho mes después de la fecha de instalación.
            # Entonces en la factura se cobran los días proporcionales que corresponden al mes en curso mas un abono
            # completo que corresponde al mes siguiente.
            daily_amount = subscription_total_mount / \
                           monthrange(self.service_start_up.year, self.service_start_up.month)[1]
            # calculo los días del mes de servicio gozado
            days_enjoyed = monthrange(self.service_start_up.year, self.service_start_up.month)[1] - \
                               self.service_start_up.day + 1
            # creo el producto que representa el descuento
            self.env['sale.order.line'].create({
                'name': 'Servicio operativo desde ' + self.service_start_up.strftime('%d/%m/%Y'),
                'order_id': self.sale_order_id.id,
                'product_id': int(enjoyed_service_days_product_id),
                'price_unit': daily_amount,
                'product_uom_qty': days_enjoyed,
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Información',
                    'message': 'Se ha agregado un ítem en la orden de venta {} por los dias de servicio gozados desde la instalación.'.format(
                        self.sale_order_id.name),
                    'sticky': True,
                }
            }
        else:
            raise ValidationError("No se encontró una Orden de Venta asociada.")
