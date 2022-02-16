# -*- coding: utf-8 -*-
{
    'name': "nybble_sale_subscription_discounts",

    'summary': """
        Permit to apply globals and line by line discounts on subscriptions for 
        generate recurring invoices a limit of periods to apply global discount on recurring invoices.
        """,

    'description': """
        Permit to apply globals and line by line discounts on subscriptions for 
        generate recurring invoices a limit of periods to apply global discount on recurring invoices.
    """,

    'author': "Nybble Group",
    'website': "https://www.nybblegroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_global_discount', 'sale_subscription'],

    # always loaded
    'data': [
        'views/global_discount_views.xml',
        'views/sale_subscription_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
