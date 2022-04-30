# -*- coding: utf-8 -*-
{
    'name': "Wobin créditos",

    'summary': """
        Aplicación para administración de procesos de créditos""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Wobin",
    'website': "http://www.yourcompany.com", 

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1.4',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'web','account'],

    # always loaded
    'data': [
        'data/credit_data.xml',

        'security/credit_security.xml',
        'security/ir.model.access.csv',
        
        #'views/views.xml',
        #'views/templates.xml',
        'views/menus.xml',
        'views/params.xml',
        'views/pre_application.xml',
        'views/reports.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}