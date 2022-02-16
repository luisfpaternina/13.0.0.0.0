# -*- coding: utf-8 -*-
{
    'name': "nybble_account_payment_return_import",

    'summary': """
        Permite importar los archivos que informan los pagos de las facturas de distintas
        entidades de procesamiento de pagos.
        1. Débitos en cuenta del Banco BBVA.
        2. Débitos con tarjeta de crédito Visa para Prisma.
        """,

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
                'account_payment_return',
                'account_payment_return_import',
                'account_payment_fix',
                #'account_payment_order'
    ],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        # 'data/account_payment_method.xml',
        'views/payment_return_import_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
