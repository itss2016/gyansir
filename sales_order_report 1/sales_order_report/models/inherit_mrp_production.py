from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    has_setting = fields.Boolean(string='Has Setting', compute='_compute_has_setting', store=True)

    @api.depends('product_id.is_setting')
    def _compute_has_setting(self):
        for mo in self:
            # Check the is_setting of the product to be produced
            mo.has_setting = mo.product_id.is_setting
