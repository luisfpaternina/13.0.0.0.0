from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    late_charge = fields.Char(
        string="Late charge",
        related="company_id.late_charge",
        readonly=False,
        config_parameter='admministrative_expenses.late_charge')
    late_charge_value = fields.Float(
        string="Late charge value",
        related="company_id.late_charge_value",
        readonly=False,
        config_parameter='admministrative_expenses.late_charge_value')
    late_charge_days = fields.Integer(
        string="Late charge days",
        related="company_id.late_charge_days",
        readonly=False,
        config_parameter='admministrative_expenses.late_charge_days')
    late_fee = fields.Char(
        string="Late fee",
        related="company_id.late_fee",
        readonly=False,
        config_parameter='admministrative_expenses.late_fee')
    late_fee_value = fields.Float(
        string="Late fee value",
        related="company_id.late_fee_value",
        readonly=False,
        config_parameter='admministrative_expenses.late_fee_value')
    late_fee_days = fields.Integer(
        string="Late fee days",
        related="company_id.late_fee_days",
        readonly=False,
        config_parameter='admministrative_expenses.late_fee_days')
    block_name = fields.Char(
        string="Name",
        related="company_id.block_name",
        readonly=False,
        config_parameter='admministrative_expenses.block_name')
    block_value = fields.Float(
        string="Value",
        related="company_id.block_value",
        readonly=False,
        config_parameter='admministrative_expenses.block_value')
    block_rejected = fields.Char(
        string="Name",
        related="company_id.block_rejected",
        readonly=False,
        config_parameter='admministrative_expenses.block_rejected')
    rejected_value = fields.Float(
        string="Value",
        related="company_id.rejected_value",
        readonly=False,
        config_parameter='admministrative_expenses.rejected_value')

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('late_charge', self.late_charge)
        self.env['ir.config_parameter'].sudo().set_param('late_fee', self.late_fee)
        self.env['ir.config_parameter'].sudo().set_param('late_charge_value', self.late_charge_value)
        self.env['ir.config_parameter'].sudo().set_param('late_fee_value', self.late_fee_value)
        self.env['ir.config_parameter'].sudo().set_param('block_name', self.block_name)
        self.env['ir.config_parameter'].sudo().set_param('block_value', self.block_value)
        self.env['ir.config_parameter'].sudo().set_param('block_rejected', self.block_rejected)
        self.env['ir.config_parameter'].sudo().set_param('rejected_value', self.rejected_value)
        return res
