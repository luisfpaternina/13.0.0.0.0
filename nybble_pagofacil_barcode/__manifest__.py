# -*- coding: utf-8 -*-
{
    'name': "nybble_pagofacil_barcode",

    'summary': """
        Agrega código de barras a las facturas para poder cobrarlas mediante pagofacil""",

    'description': """
        Agrega código de barras a las facturas para poder cobrarlas mediante pagofacil.
    """,

    'author': "Nybble Group",
    'website': "https://www.nybblegroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'l10n_ar_edi'],

    # always loaded
    'data': [
        'views/report_invoice.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
