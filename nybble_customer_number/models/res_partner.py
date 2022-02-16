# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PartnerCustomerType(models.Model):
    _description = 'Tipo de Cliente'
    _name = 'res.partner_customer_type'

    name = fields.Char(string='Nombre')
    active = fields.Boolean('Activo', default=True)

class Partner(models.Model):
    _inherit = 'res.partner'

    # _sql_constraints = [
    #     ('customer_number_uniq', 'unique(customer_number)', 'El número de cliente debe ser único!')
    # ]

    customer_number = fields.Integer(string="Número de cliente", index=True)

    customer_next_number = fields.Integer(string='Próximo número de cliente', required=True, copy=False,
                                          default=lambda self: self.env['ir.sequence'].search(
                                              [('code', '=', 'res.partner.customer.number')]).mapped(
                                              'number_next_actual')[0])

    customer_type = fields.Many2one('res.partner_customer_type', string="Tipo de Cliente")

    @api.model
    def create(self, vals):
        # agrego lógica para asignar número de cliente
        # si company_type = 'company'  customer_number debe ser 0
        # si company_type = 'person'  customer_number debe ser el siguiente número de la secuencia
        if vals.get('company_type') == 'company':
            vals['customer_number'] = 0
        if vals.get('company_type') == 'person':
            vals['customer_number'] = self.env['ir.sequence'].next_by_code('res.partner.customer.number')
        return super(Partner, self).create(vals)

    # defino método para asignar número de cliente solo cuando company_type = 'person', si company_type = 'company' el customer number es 0
    @api.onchange('company_type')
    def _onchange_company_type(self):
        if self.company_type == 'company':
            self.customer_next_number = 0
        if self.company_type == 'person':
            self.customer_next_number = \
            self.env['ir.sequence'].search([('code', '=', 'res.partner.customer.number')]).mapped(
                'number_next_actual')[0]
