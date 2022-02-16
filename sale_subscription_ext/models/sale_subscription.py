# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    city = fields.Char(string="City")

    @api.onchange('partner_id')
    def onchange_partner(self):
        for record in self:
            if record.partner_id:
                record.city = record.partner_id.city
