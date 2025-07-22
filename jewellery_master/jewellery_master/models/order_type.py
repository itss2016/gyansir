from odoo import models, fields, api


class OrderType(models.Model):
    _name = "order.type"
    _description = "Order Type"
    _rec_name = "order_type"

    order_type = fields.Char(string="Order Type", required=True)

