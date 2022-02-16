# -*- coding: utf-8 -*-
{
    'name': "nybble_sale_subscription_batch_fe_edi",

    'summary': """
        Facturación recurrente de suscripciones por lotes AFIP Odoo EE""",

    'description': """
        
    """,

    'author': "NybbleGroup",
    'website': "https://www.nybblegroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_subscription', 'l10n_ar_edi', 'nybble_customer_number'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_subscription_views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
