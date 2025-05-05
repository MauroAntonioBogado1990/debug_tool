{
    'name': 'Debug Tool',
    'version': '17.0',
    'category': 'Tools',
    'author':'Mauro Bogado',
    'summary': 'Herramienta para debugging de datos y funciones en Odoo',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/debug_tool_views.xml',
    ],
    'installable': True,
    'application': False,
}   