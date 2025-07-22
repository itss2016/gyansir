{
    'name': 'Customer Product Code',
    'version': '1.0',
    'depends': ['base', 'sale', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/customer_product_code_views.xml',
        'views/inherit_sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
