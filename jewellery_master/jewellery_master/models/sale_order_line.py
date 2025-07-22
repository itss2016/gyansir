from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # gross_weight = fields.Float(string="Gross Weight", digits=(16, 3))
    # net_weight = fields.Float(string="Net Weight", digits=(16, 3))
    # fineness = fields.Float(string="Fineness", related="product_id.metal.fineness_ids.fineness", store=True, readonly=True)
    product_collection = fields.Many2one(
        "collection.master",
        string="Collection",
        related="product_id.collection_id",
        store=True,
        readonly=True)
    # metal_colour = fields.Many2one(
    #     "colour.master",
    #     string="Metal Color",
    #     related="product_id.color",
    #     store=True,
    #     readonly=True
    # )
    metal_product = fields.Many2one(
        "metal.master",
        string="Metal",
        related="product_id.metal",
        store=True,
        readonly=True
    )
    product_size = fields.Many2one(
        "size.master",
        string="Size",
        store=True,
        readonly=False

    )
    category_id = fields.Many2one('product.category', string='Item', related='product_id.categ_id',
                                  readonly=True)

    # fine_weight = fields.Float(string="Fine Wt", compute="_compute_fine_weight", store=True, digits=(16, 4))
    remark_ids = fields.Char(string="Remarks", store=True)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        """When a product is selected, set the size but allow manual changes."""
        if self.product_id:
            self.product_size = self.product_id.size_id

    # @api.depends("net_weight", "fineness")
    # def _compute_fine_weight(self):
    #     for line in self:
    #         line.fine_weight = line.net_weight * line.fineness if line.fineness else 0
