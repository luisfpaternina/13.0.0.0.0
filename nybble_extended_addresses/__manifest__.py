# -*- coding: utf-8 -*-
{
    'name': "nybble_extended_addresses",

    'summary': """
        Extiende funcionalidad para direcciones de partners""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Nybble Group",
    'website': "http://www.nybblegroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_address_extended', 'base_location', 'base_location_geonames_import', 'l10n_ar'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/res_street_views.xml',
        'views/res_neighborhood_views.xml',
        # 'views/templates.xml',
        'data/res_street.xml',
        'data/res_neighborhood.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
