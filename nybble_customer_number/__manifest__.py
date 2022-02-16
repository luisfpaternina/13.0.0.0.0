# -*- coding: utf-8 -*-
{
    'name': "nybble_customer_number",

    'summary': """
        Agrega un campo para usar como número de cliente externo a Odoo para usar cuando se migran usuarios
        de otros sistemas""",

    'description': """
        Agrega un campo para usar como número de cliente externo a Odoo para usar cuando se migran usuarios.
        Implementa funcionalidad para que el número de cliente externo se genere automáticamente.
    """,

    'author': "Nybble Group",
    'website': "https://www.nybblegroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web_map', 'nybble_extended_addresses'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'data/res_partner.xml',
        'views/res_partner_views.xml',
        # 'views/templates.xml',
        'security/ir.model.access.csv',
        'data/res_partner_customer_type.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    # creamos secuencia para generar números de cliente externo antes de
    'pre_init_hook': 'add_sequence_hook',
}
