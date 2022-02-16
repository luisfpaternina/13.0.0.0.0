from odoo import fields, models, api, _


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    # TODO: Implement global discount on sale subscription
    # global_discount_ids = fields.Many2many(
    #     comodel_name="global.discount",
    #     column1="subscription_id",
    #     column2="global_discount_id",
    #     string="Subscription Global Discounts",
    #     track_visibility="always"
    # )
    #
    # applied_discounts_counter = fields.Integer(string="Discounts Applied", default=0,
    #                                    help="Number of times that invoices were generated applying with this discount")

    def _prepare_invoice_line(self, line, fiscal_position, date_start=False, date_stop=False):
        """
        Override to:
            1. Increase applied discount counter
            2. Check the validity of the discount. If it is not valid anymore, remove it from the line

        :param line: subscription line
        :param fiscal_position: Partner fiscal position
        :param date_start: Subscription invoice period start date
        :param date_stop: Subscription invoice period stop date
        :return: super._prepare_invoice_line() vals with subscription line info
        """
        if line.discount_id:
            line.applied_discounts_counter += 1
            if line.applied_discounts_counter > line.discount_id.recurring_invoice_period_limit and line.discount_id.recurring_invoice_period_limit >= 0:
                self.message_post(body=_("Discount {} was removed because it was applied {} times".format(
                    line.discount_id.display_name,
                    line.discount_id.recurring_invoice_period_limit)))  # Log message on chatter - TODO: translate
                line.discount_id = False  # Remove discount from the list
                line.applied_discounts_counter = 0  # Reset counter
                line.discount = 0.0  # Reset discount
                line.name = line.product_id.display_name  # Reset name to product display_name
        return super(SaleSubscription, self)._prepare_invoice_line(line, fiscal_position, date_start, date_stop)

    # TODO : Implement global discount on sale subscription
    # def _prepare_invoice_data(self):
    #     vals = super(SaleSubscription, self)._prepare_invoice_data()
    #     # vals['global_discount_ids'] = [(6, 0, self.global_discount_ids.ids)]
    #     vals['global_discount_ids'] = self.global_discount_ids.ids
    #     return vals

class SaleSubscriptionLine(models.Model):
    _inherit = "sale.subscription.line"

    discount_id = fields.Many2one(
        comodel_name="global.discount",
        string="Line Discounts",
        track_visibility="always"
    )

    applied_discounts_counter = fields.Integer(string="Discounts Applied", default=0,
                                       help="Number of times that invoices were generated with this discount in the subscription line")

    @api.onchange('discount_id')
    def on_change_discount_id(self):
        """
        This method is used to apply line discounts to the subscription lines
        """
        self.discount = 0.0
        self.name = self.product_id.name
        if self.discount_id:
            self.applied_discounts_counter = 0
            self.discount = self.discount_id.discount
            self.name = self.product_id.display_name + " - " + self.discount_id.display_name
