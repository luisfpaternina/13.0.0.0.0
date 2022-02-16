# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_cancel(self):
        # Al cancelar una orden de venta, borramos las suscripciones que se generaron automáticamente.
        # Otra opción era pasarla a estado borrador pero se decidió eliminarla.
        for order in self:
            sub = self.env['sale.order.line'].read_group(
                [('order_id', '=', order.id), ('subscription_id', '!=', False)],
                ['subscription_id'], ['subscription_id'])
            for s in sub:
                subscription = self.env['sale.subscription'].browse(s['subscription_id'][0])
                # subscription.write({'stage_id': 1}) # pasamos la suscripción generada a estado borrador
                subscription.unlink() # borramos la suscripción
        return super(SaleOrder, self).action_cancel()

    def action_confirm(self):
        # validacíon para que los productos de la suscripción siempre pertenezcan a la misma plantilla
        if len(self.order_line.product_id.subscription_template_id) > 1:
            raise UserError(
                "Los productos de las líneas del pedido que generan suscripciones, deben pertenecer a la misma \n"
                "plantilla de suscripción. Por favor verifique y vuelva a intentar.")
        return super(SaleOrder, self).action_confirm()
