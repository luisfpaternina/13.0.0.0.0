from odoo import models, fields, api, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    late_charge = fields.Char(
        string="Late charge")
    late_charge_value = fields.Float(
        string="Late charge value")
    late_charge_days = fields.Integer(
        string="Late charge days")
    late_fee = fields.Char(
        string="Late fee")
    late_fee_value = fields.Float(
        string="Late fee value")
    late_fee_days = fields.Integer(
        string="Late fee days")
    block_name = fields.Char(
        string="Name")
    block_value = fields.Float(
        string="Value")
    block_rejected = fields.Char(
        string="Name")
    rejected_value = fields.Float(
        string="Value")
