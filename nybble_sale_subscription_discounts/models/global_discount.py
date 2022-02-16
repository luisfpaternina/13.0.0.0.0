from odoo import models, fields, api, _

class GlobalDiscount(models.Model):
    _inherit = "global.discount"

    recurring_invoice_period_limit = fields.Integer(string="Recurring Invoice Period Limit", default=0,
                                                    help="The number of recurring billing periods that the discount \
                                                    will have an effect on. Enter negative value to make the \
                                                    discount apply to all recurring billing periods.")

    def name_get(self):
        result = []
        for one in self:
            result.append((one.id, "{} ({:.2f}%) por {} períodos".format(one.name, one.discount, one.recurring_invoice_period_limit)))
        return result
