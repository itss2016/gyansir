{
    'name': 'Sales Order Report',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Custom Sales Order Report - Read-Only',
    'author': 'Gaurav Goswami',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_report_view.xml',
        'views/sale_order_report_menu.xml',
        'views/create_mo_action.xml',
        'views/create_mo_wizard_views.xml',
        'views/inherit_sale_order_line_views.xml',

    ],
    'installable': True,
    'application': False,
}
