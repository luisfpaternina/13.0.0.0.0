# -*- coding: utf-8 -*-
{
    'name': "Davitel reports",

    'summary': """This module adds fields in the invoice form""",

    'author': "NybbleGroup",

    'website': "",

    'contributors': ['NybbleGroup'],

    'category': 'reports',

    'version': '14.0.0.1',

    'depends': [
        'account_accountant',
        'account',
        'account_payment_partner',
        'nybble_extended_addresses',
    ],

    'data': [

        "reports/inherit_invoice.xml",
      
    ],
    
    'installable': True,
}
