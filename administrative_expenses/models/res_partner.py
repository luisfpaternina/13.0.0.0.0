from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_blocking = fields.Boolean(
        string="Blocking",
        compute="_compute_check_category_id")

    @api.depends('category_id')
    def _compute_check_category_id(self):
        for record in self:
            record.is_blocking = True if record.category_id and record.category_id[0].name  == 'BLOQUEO' else False
