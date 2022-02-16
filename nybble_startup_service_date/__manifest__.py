# -*- coding: utf-8 -*-
{
    'name': "nybble_startup_service_date",

    'summary': """
        Permite calcular los días de servicio gozados basado en la fecha de startup del servicio en el cliente
        y agrega un item de descuento en la orden de venta con el monto calculado en base a los servicios de 
        suscripción y los dias que no tuvo servicio.
        """,

    'description': """
        Agrega un campo para establecer cuando fue la fecha en que el servicio queda operativo para el cliente.
        Al quedar establecida la fecha de inicio del servicio, se calcula el número de días de servicio gozados. 
    """,

    'author': "Nybble Group",
    'website': "https://www.nybblegroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'industry_fsm'],

    # always loaded
    'data': [
        'views/project_task_views.xml',
        'views/res_config_settings.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
