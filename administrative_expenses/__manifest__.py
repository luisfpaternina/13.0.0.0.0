{
    'name': 'Administrative expenses',

    'summary': """
        This module add one line in subscription lines when payment is letter than
        due date""",

    'description': """
        When a customer pays late, 
        is in arrears or the service is blocked, 
        a penalty charge is added to the following month's bill.
        Since every month there are several clients to whom these charges have to be added, 
        they could be added massively so that they would later appear automatically in the next invoice that is issued in subscriptions.
    """,

    'version': '13.0.1.0',

    'author': "Nybble group",

    'contributors': ['Luis Felipe Paternina'],

    'website': "https://www.nybblegroup.com/",

    'category': 'Subscriptions',

    'depends': [

        'account_accountant',
        'sale_management',
        'sale_subscription',
        'contacts',
        'base',
        'nybble_account_payment_return_import',
        'account_payment_return',

    ],

    'data': [

        'data/account.tax.csv',
        'data/product.template.csv',
        'views/account_move.xml',
        'views/res_partner.xml',
        'views/res_config_settings.xml',
                   
    ],
    'installable': True
}
