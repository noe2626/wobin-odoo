# -*- coding: utf-8 -*-
{
    'name': "Báscula",

    'summary': """
        Modulo para control de pesadas de báscula, registro de boletas y análisis de calidad""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Wobin",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'purchase', 'sale', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/bascula_security.xml',
        
        'views/views.xml',
        'views/templates.xml',

        'views/print.xml',
        'views/analysis.xml',
        'views/tickets.xml',
        'views/reports.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}