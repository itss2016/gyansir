from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    customer_product_code_id = fields.Many2one('customer.product.code', string='Customer Code')

    @api.onchange('customer_product_code_id')
    def _onchange_customer_product_code_id(self):
        """
        When customer code is selected, the product should auto-fill.
        """
        if self.customer_product_code_id:
            self.product_id = self.customer_product_code_id.product_id

    @api.onchange('product_id', 'order_id.partner_id')
    def _onchange_product_id_or_customer(self):
        """
        When product or customer changes, the customer code should auto-fill.
        """
        if self.product_id and self.order_id.partner_id:
            customer_code = self.env['customer.product.code'].search([
                ('customer_id', '=', self.order_id.partner_id.id),
                ('product_id', '=', self.product_id.id)
            ], limit=1)
            self.customer_product_code_id = customer_code.id if customer_code else False

    @api.onchange('order_id.partner_id')
    def _onchange_customer_only(self):
        """
        When customer is changed, customer code should refresh for selected product.
        """
        for line in self:
            if line.product_id:
                customer_code = self.env['customer.product.code'].search([
                    ('customer_id', '=', line.order_id.partner_id.id),
                    ('product_id', '=', line.product_id.id)
                ], limit=1)
                line.customer_product_code_id = customer_code.id if customer_code else False
