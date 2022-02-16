from odoo import models, fields, api, _

class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    @api.onchange('name')
    def _upper_name(self):        
        self.name = self.name.upper() if self.name else False
