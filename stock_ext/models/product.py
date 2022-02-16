from odoo import models, fields, api, _
import logging


class ProductProduct(models.Model):
    _inherit = 'product.product'

    codigo_ncm = fields.Char(string="Codigo NCM")


    @api.onchange('codigo_ncm')
    def _onchange_ncm(self):
        product_obj = self.env['product.template'].search([('name', '=', self.name)],limit=1)
        if product_obj:
            self.codigo_ncm = self.product_obj.codigo_ncm
        else:
            self.codigo_ncm = False





class ProductTemplate(models.Model):
    _inherit = 'product.template'

    codigo_ncm = fields.Char(string="Codigo NCM")


    @api.onchange('codigo_ncm')
    def _onchange_ncm(self):
        product_obj = self.env['product.product'].search([('name', '=', self.name)],limit=1)
        if product_obj:
            self.codigo_ncm = self.product_obj.codigo_ncm
        else:
            self.codigo_ncm = False
