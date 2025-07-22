from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrderReport(models.Model):
    _name = 'sale.order.report'
    _description = 'Sales Order Report'
    _auto = False  # Read-only model

    order_id = fields.Many2one('sale.order', string="Order No", readonly=True)
    customer_id = fields.Many2one('res.partner', string="Customer", readonly=True)
    date_order = fields.Datetime(string="Date", readonly=True)
    product_id = fields.Many2one('product.product', string="Product", readonly=True)
    product_uom_qty = fields.Float(string="Order Quantity", readonly=True)
    qty_delivered = fields.Float(string="Delivered Quantity", readonly=True)
    remaining_quantity = fields.Float(string="Remaining Quantity", readonly=True)

    gross_weight = fields.Float(string="Gross Weight", readonly=True)
    net_weight = fields.Float(string="Net Weight", readonly=True)

    bom_id = fields.Many2one('mrp.bom', string="BOM", readonly=True)
    process_bom_id = fields.Many2one('mrp.bom', string="Process BOM", readonly=True)

    price_unit = fields.Float(string="Unit Price", readonly=True)
    price_subtotal = fields.Float(string="Subtotal", readonly=True)

    mo_qty_manufactured = fields.Float(string="Order Released", compute="_compute_manufactured_qty", store=False)
    mo_remaining_qty = fields.Float(string="To Released", compute="_compute_manufactured_qty", store=False)

    def init(self):
        """ Create or Replace the SQL View """
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW sale_order_report AS (
                SELECT 
                    sol.id AS id, 
                    so.id AS order_id,
                    so.partner_id AS customer_id,
                    so.date_order AS date_order,
                    sol.product_id AS product_id,
                    sol.product_uom_qty AS product_uom_qty,
                    sol.qty_delivered AS qty_delivered,                   
                    sol.price_unit AS price_unit,
                    sol.price_subtotal AS price_subtotal,                   
                    (sol.product_uom_qty - sol.qty_delivered) AS remaining_quantity,
                    (sol.product_uom_qty * pt.gross_weight) AS gross_weight,
                    (sol.product_uom_qty * pt.net_weight) AS net_weight,
                    sol.process_bom_id AS process_bom_id
                FROM sale_order_line sol
                JOIN sale_order so ON sol.order_id = so.id
                JOIN product_product pp ON sol.product_id = pp.id
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                WHERE sol.product_uom_qty > sol.qty_delivered
                AND so.state NOT IN ('cancel', 'draft', 'sent')
            )
        """)

    @api.depends('order_id', 'product_id')
    def _compute_manufactured_qty(self):
        for rec in self:
            mo_qty = 0.0
            if rec.order_id and rec.product_id:
                mo_list = self.env['mrp.production'].search([
                    ('origin', '=', rec.order_id.name),
                    ('product_id', '=', rec.product_id.id),
                    ('state', 'not in', ['cancel'])
                ])
                mo_qty = sum(mo.product_qty for mo in mo_list)
            rec.mo_qty_manufactured = mo_qty
            rec.mo_remaining_qty = rec.remaining_quantity - mo_qty

