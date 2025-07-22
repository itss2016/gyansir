{
    'name': 'Iyosa MRP Weight',
    'version': '1.0',
    'summary': 'Add Gross and Net Weight to Products and Manufacturing Orders',
    'author': 'Iyosa Infotech/Gaurav',
    'depends': ['product', 'mrp'],
    'data': [
        'views/product_template_views.xml',
        'views/mrp_production_views.xml',
        # 'views/mrp_bom_line_views.xml',

    ],
    'installable': True,
    'application': False,
}
