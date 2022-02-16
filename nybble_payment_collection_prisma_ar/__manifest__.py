# -*- coding: utf-8 -*-
{
    'name': "nybble_payment_collection_prisma_ar",

    'summary': """
        Permite generar archivos de texto plano para informar la cobranza de facturas a PRISMA medios de pago.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Nybble Group",
    'website': "https://www.nybblegroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'account_payment_order',
                'account_payment_return_import',
                'account_banking_mandate',
                ],

    # always loaded
    'data': [
        # 'data/account_payment_method.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
