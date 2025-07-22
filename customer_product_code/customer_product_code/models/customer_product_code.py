from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CustomerProductCode(models.Model):
    _name = 'customer.product.code'
    _description = 'Customer Product Code'
    _rec_name = 'customer_code'

    customer_id = fields.Many2one('res.partner', string='Customer', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True, ondelete='cascade')
    customer_code = fields.Char(string='Customer Product Code', required=True)

    @api.constrains('customer_id', 'product_id')
    def _check_unique_customer_product(self):
        for record in self:
            duplicates = self.search([
                ('customer_id', '=', record.customer_id.id),
                ('product_id', '=', record.product_id.id),
                ('id', '!=', record.id)
            ])
            if duplicates:
                raise ValidationError(
                    f'This customer already has a product code assigned for "{record.product_id.display_name}".'
                )

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.customer_code}"
            result.append((record.id, name))
        return result


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_code_count = fields.Integer(string='Customer Code Count', compute='_compute_customer_code_count')

    def action_view_customer_product_codes(self):
        for partner in self:
            return {
                'name': 'Customer Codes',
                'type': 'ir.actions.act_window',
                'res_model': 'customer.product.code',
                'view_mode': 'list,form',
                'domain': [('customer_id', '=', partner.id)],
                'context': {'default_customer_id': partner.id},
                'target': 'current',
            }

    def _compute_customer_code_count(self):
        for partner in self:
            partner.customer_code_count = self.env['customer.product.code'].search_count([('customer_id', '=', partner.id)])


class ProductProduct(models.Model):
    _inherit = 'product.product'

    customer_code_count = fields.Integer(string='Customer Code Count', compute='_compute_customer_code_count')

    def action_view_customer_product_codes(self):
        for product in self:
            return {
                'name': 'Customer Codes',
                'type': 'ir.actions.act_window',
                'res_model': 'customer.product.code',
                'view_mode': 'list,form',
                'domain': [('product_id', '=', product.id)],
                'context': {'default_product_id': product.id},
                'target': 'current',
            }

    def _compute_customer_code_count(self):
        for product in self:
            product.customer_code_count = self.env['customer.product.code'].search_count([('product_id', '=', product.id)])





class ProductTemplate(models.Model):
    _inherit = 'product.template'

    customer_code_count = fields.Integer(string='Customer Code Count', compute='_compute_customer_code_count')

    def action_view_customer_product_codes(self):
        for template in self:
            products = self.env['product.product'].search([('product_tmpl_id', '=', template.id)])
            return {
                'name': 'Customer Codes',
                'type': 'ir.actions.act_window',
                'res_model': 'customer.product.code',
                'view_mode': 'list,form',
                'domain': [('product_id', 'in', products.ids)],
                'context': {'default_product_id': products[:1].id if products else False},
                'target': 'current',
            }

    def _compute_customer_code_count(self):
        for template in self:
            products = self.env['product.product'].search([('product_tmpl_id', '=', template.id)])
            template.customer_code_count = self.env['customer.product.code'].search_count([('product_id', 'in', products.ids)])
