from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_type = fields.Many2one("order.type", string="Order Type", store="True")