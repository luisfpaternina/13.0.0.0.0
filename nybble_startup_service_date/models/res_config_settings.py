# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enjoyed_service_days_product_id = fields.Many2one('product.template',
                                                      string='Producto para descuentos en suscripciones',
                                                      domain=[('type', '=', 'service')],
                                                      help="Define el producto que se usará para agregar en las \
                                                       órdenes de ventas que contengan productos de una suscripción\
                                                        y que tengan días de servicio gozados al dar de alta un servicio.")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            enjoyed_service_days_product_id=int(self.env['ir.config_parameter'].sudo().get_param(
                'nybble_startup_service_date.enjoyed_service_days_product_id'),
            ))
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        field1 = self.enjoyed_service_days_product_id and self.enjoyed_service_days_product_id.id or False
        param.set_param('nybble_startup_service_date.enjoyed_service_days_product_id', field1)
