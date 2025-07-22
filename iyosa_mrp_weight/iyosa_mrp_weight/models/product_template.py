from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    gross_weight = fields.Float(string="Gross Weight", digits=(16, 3))
    net_weight = fields.Float(string="Net Weight", digits=(16, 3))
    component_type = fields.Selection([
        ('wip', 'WIP'),
        ('stone', 'Stone'),
        ('gold', 'Gold'),
        ('wax', 'Wax'),
        ('finding', 'Finding'),
        ('setting', 'Setting')
    ], string="Metal Type")
    is_setting = fields.Boolean(string='Is Setting')
    fineness = fields.Float(string='Fineness (%)', digits=(6, 3))
    wastage_percent = fields.Float(string="Wastage (%)")



class ProductProduct(models.Model):
    _inherit = 'product.product'

    gross_weight = fields.Float(related='product_tmpl_id.gross_weight', string="Gross Weight", store=True, digits=(16, 3))
    net_weight = fields.Float(related='product_tmpl_id.net_weight', string="Net Weight", store=True, digits=(16, 3))
    component_type = fields.Selection(related='product_tmpl_id.component_type', string="Type", store="True")
    is_setting = fields.Boolean(related='product_tmpl_id.is_setting', string="Is Setting", store="True")
    wastage_percent = fields.Float(string="Wastage (%)")
