from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    metal = fields.Many2one("metal.master", string="Metal", store="True")
    # fineness = fields.Float(string="Fineness", related="metal.fineness_ids.fineness", store=True, readonly=True)
    # color = fields.Many2one("colour.master", string='Color', store="True")
    collection_id = fields.Many2one("collection.master", string='Collection', store="True")
    size_id = fields.Many2one("size.master", string='Size', store="True")


class ProductProduct(models.Model):
    _inherit = "product.product"

    metal = fields.Many2one("metal.master", string="Metal", related="product_tmpl_id.metal", store=True, readonly=False)
    # fineness = fields.Float(string="Fineness", related="product_tmpl_id.fineness", store=True, readonly=True)
    # color = fields.Many2one("colour.master", string='Color', related="product_tmpl_id.color", store=True, readonly=False)
    collection_id = fields.Many2one("collection.master", string='Collection', related="product_tmpl_id.collection_id", store=True, readonly=False)
    size_id = fields.Many2one("size.master", string='Size', related="product_tmpl_id.size_id", store=True, readonly=False)