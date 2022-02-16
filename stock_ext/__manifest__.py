{
    'name': 'Stock ext',

    'summary': """
        This module add fields in stock in the models product.product and product.template""",

    'version': '13.0.1.0',

    'author': "Nybble group",

    'contributors': ['Luis Felipe Paternina'],

    'website': "",

    'category': 'Stock',

    'depends': [

        'sale_management',
        'stock',
        #'l10n_ar_afipws_fe',

    ],

    'data': [
       
        'views/product.xml',
                   
    ],
    'installable': True
}
