from odoo import models, fields, api, _
from datetime import datetime, date
import logging

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Variables
    is_validate = fields.Boolean(
        string="Validate",
        compute="_validate_subscription")
    is_validate_date = fields.Boolean(
        string="Validate dates",
        compute="_validate_dates")
    aditional_value = fields.Float(
        string="Aditional value",
        compute="_calculate_aditional_value")
    aditional_payment_date = fields.Date(
        string="Payment date")
    expense_product = fields.Many2one(
        'product.template',
        string="Product",
        compute="add_administrative_expense_product")
    days_difference = fields.Integer(
        string='Days',
        compute="_compute_difference")
    expense_name = fields.Char(
        string="Expense name",
        compute="_get_expenses_names")
    is_blocking = fields.Boolean(
        string="Blocking",
        related="partner_id.is_blocking")
    register_date = fields.Date(
        string="Register date")


    @api.depends('days_difference')
    def _get_expenses_names(self):
        # Función para traer los datos de la parametrización(datos) realizada en res.config.settings
        for record in self:
            settings_late_charge = self.env.company.late_charge
            late_charge_value = self.env.company.late_charge_value
            settings_late_fee = self.env.company.late_fee
            block_name = self.env.company.block_name
            block_rejected = self.env.company.block_rejected
            if record.is_blocking:
                record.expense_name = block_name
            elif record.days_difference < 30:
                record.expense_name = settings_late_charge
            elif record.days_difference >= 30:
                record.expense_name = settings_late_fee
            else:
                record.expense_name = ' '

    @api.depends(
        'aditional_payment_date',
        'invoice_date_due')
    def _compute_difference(self):
        # Función para calcular los días de mora
        for rec in self:
            if rec.register_date and rec.invoice_date_due:
                rec.days_difference = (rec.register_date - rec.invoice_date_due).days
            else:
                rec.days_difference = 0

    @api.depends('name')
    def add_administrative_expense_product(self):
        # Función para traer el producto gasto administrativo el cual se carga en la data del modulo
        product_obj = self.env['product.template'].search([('name', '=', 'Gasto administrativo')])
        if product_obj:
            self.expense_product = product_obj.id
        else:
            self.expense_product = False

    @api.onchange(
        'aditional_payment_date',
        'invoice_date_due',
        'state',
        'invoice_payment_term_id',
        'invoice_date',
        'name')
    def _calculate_payment_date(self):
        # Función para consultar el valor de la fecha de pago en el wizard de account.payment
        payment_obj = self.env['account.payment'].search(
            [('communication', '=', self.name)], limit=1)
        if payment_obj:
            self.aditional_payment_date = payment_obj.payment_date
        else:
            self.aditional_payment_date = False

    @api.depends(
        'register_date',
        'invoice_date_due')
    def _calculate_aditional_value(self):
        # Calculo del valor del gasto administrativo dependiendo de los días de mora
        late_charge_value = self.env['ir.config_parameter'].sudo().get_param('administrative_expenses.late_charge_value') or False
        charge_value = late_charge_value / 100
        late_charge_value = self.env.company.late_charge_value
        charge_value = late_charge_value / 100
        late_fee_value = self.env.company.late_fee_value
        fee_value = late_fee_value / 100
        if self.register_date and self.invoice_date_due:
            if self.register_date > self.invoice_date_due and self.days_difference < 30:
                self.aditional_value = self.amount_untaxed * charge_value
            elif self.register_date > self.invoice_date_due and self.days_difference >= 30:
                self.aditional_value = self.amount_untaxed * fee_value
            else:
                self.aditional_value = 0.0
        else:
            self.aditional_value = 0.0

    @api.depends(
        'register_date',
        'invoice_date_due',
        'state',
        'invoice_payment_term_id',
        'invoice_date',
        'name')
    def _validate_dates(self):
        # Función para comparar fechas: fecha de pago vs plazo de pago
        for record in self:
            if record.register_date and record.invoice_date_due:
                if record.register_date > record.invoice_date_due:
                    record.is_validate_date = True
                elif record.register_date <= record.invoice_date_due:
                    record.is_validate_date = False
                else:
                    record.is_validate_date = False
            else:
                record.is_validate_date = False

    def _validate_subscription(self):
        # Función para agregar o eliminar líneas en la suscripción dependiendo el gasto administrativo
        for record in self:
            if record.invoice_payment_state == 'paid' and record.is_blocking:
                sale_obj = record.env['sale.order'].search([('name', '=', record.invoice_origin)])
                subscription_obj = record.env['sale.subscription'].search([])
                block_value = self.env.company.block_value
                for s in subscription_obj:
                    if sale_obj:
                        record.is_validate = True
                        if s in sale_obj.order_line.subscription_id:
                            s.display_name
                            c = 1
                            for line in s.recurring_invoice_line_ids:
                                range_number = len(s.recurring_invoice_line_ids)
                                if c < range_number:
                                    quantity = 1
                                    price_unit = 0
                                else:
                                    quantity = 1
                                    price_unit = block_value

                                vals = {
                                    'product_id': record.expense_product.id,
                                    'name': record.expense_name,
                                    'price_unit': price_unit,
                                    'quantity': quantity,
                                    'uom_id': s.recurring_invoice_line_ids.uom_id.id,
                                    }
                                line.write(vals)
                                c = c + 1
                            break
                        else:
                            record.is_validate = False
                    else:
                        record.is_validate = False
            elif record.invoice_payment_state == 'paid' and record.is_validate_date:
                sale_obj = record.env['sale.order'].search([('name', '=', record.invoice_origin)])
                subscription_obj = record.env['sale.subscription'].search([])
                for s in subscription_obj:
                    if sale_obj:
                        record.is_validate = True
                        if s in sale_obj.order_line.subscription_id:
                            s.display_name
                            products = []
                            for rc in s.recurring_invoice_line_ids:
                                products.append(rc.product_id.name)
                            if 'Gasto administrativo' not in products:
                                vals = {
                                'recurring_invoice_line_ids': [(0, 0, {
                                    'product_id': record.expense_product.id,
                                    'name': record.expense_name,
                                    'price_unit': record.aditional_value,
                                    'quantity': 1,
                                    'uom_id': s.recurring_invoice_line_ids.uom_id.id,
                                    })]
                                }
                                s.write(vals)
                            else:
                                record.is_validate = False

                        else:
                            record.is_validate = False
                    else:
                        record.is_validate = False
            elif record.invoice_payment_state == 'paid' and record.is_validate_date == False:
                sale_obj = record.env['sale.order'].search([('name', '=', record.invoice_origin)])
                subscription_obj = record.env['sale.subscription'].search([])
                for s in subscription_obj:
                    if sale_obj:
                        record.is_validate = True
                        if s in sale_obj.order_line.subscription_id:
                            s.display_name
                            for sus_line in s.recurring_invoice_line_ids:
                                if sus_line.product_id.name == 'Gasto administrativo':
                                    sus_line.unlink()
                                    record.is_validate = False
                                else:
                                    record.is_validate = False
                        else:
                            record.is_validate = False
                    else:
                        record.is_validate = False
            else:
                record.is_validate = False
