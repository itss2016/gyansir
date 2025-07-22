from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    gross_weight = fields.Float(string='Gross Weight', digits=(16, 3), compute='_compute_weights', store=True)
    net_weight = fields.Float(string='Net Weight', digits=(16, 3), compute='_compute_weights', store=True)

    bom_id = fields.Many2one(
        'mrp.bom',
        string="BOM",
        domain="[('product_tmpl_id', '=', product_template_id)]")

    process_bom_id = fields.Many2one(
        'mrp.bom',
        string="Process"
    )

    fineness = fields.Float(string='Fineness', digits=(16, 3))
    # fine_weight = fields.Float(string='Fine Weight', digits=(16, 3))
    wastage_percent = fields.Float(string='Wastage', digits=(16, 2))
    fine_weight = fields.Float(string='Fine Weight', digits=(16, 3),compute="_compute_fine_weight", store=True)
    cost = fields.Float(string='Cost(BOM)', compute='_compute_cost', store=True)
    product_image = fields.Binary(string='Image', related='product_id.image_1920', readonly=True)





    # @api.depends('product_id', 'product_uom_qty')
    # def _compute_weights(self):
    #     for line in self:
    #         gross = line.product_id.gross_weight or 0.0
    #         net = line.product_id.net_weight or 0.0
    #         qty = line.product_uom_qty or 0.0
    #         line.gross_weight = gross * qty
    #         line.net_weight = net * qty

    @api.onchange('product_id')
    def _onchange_product_id_set_fineness(self):
        for line in self:
            if line.product_id:
                line.fineness = line.product_id.product_tmpl_id.fineness
            else:
                line.fineness = 0.0

    @api.depends('bom_id', 'product_uom_qty', 'fineness', 'product_id')
    def _compute_weights(self):
        for line in self:
            if line.bom_id:
                total_gross_weight_per_unit = 0.0
                total_net_weight_per_unit = 0.0

                for bom_line in line.bom_id.bom_line_ids:
                    component_product = bom_line.product_id

                    # ✅ Skip calculation for service products only ( new added change for exact calculation)
                    if component_product.type == 'service':
                        continue

                    component_qty = bom_line.product_qty  # Use the BoM component quantity as weight

                    if component_product.component_type == 'stone':
                        # Stone weight in Carats, convert to Grams
                        component_weight = component_qty * 0.2
                        total_gross_weight_per_unit += component_weight
                        # Stone weight not included in net weight
                    else:
                        # Non-stone weight directly taken as grams
                        component_weight = component_qty
                        total_gross_weight_per_unit += component_weight
                        total_net_weight_per_unit += component_weight

                # Multiply by Sales Order Line Quantity
                line.gross_weight = total_gross_weight_per_unit * line.product_uom_qty
                line.net_weight = total_net_weight_per_unit * line.product_uom_qty
                line.fine_weight = line.fineness * line.net_weight

            elif line.product_id and line.product_id.type != 'service':
                # ✅ If no BoM selected, pick weight from product's gross_weight and net_weight
                product_gross_weight = line.product_id.gross_weight or 0.0
                product_net_weight = line.product_id.net_weight or 0.0

                line.gross_weight = product_gross_weight * line.product_uom_qty
                line.net_weight = product_net_weight * line.product_uom_qty
                # line.fine_weight = line.fineness * line.net_weight

            else:
                # For service products or no product selected
                line.gross_weight = 0.0
                line.net_weight = 0.0
                # line.fine_weight = 0.0

    # @api.onchange('fineness')
    # def _onchange_fineness_recalculate_fine_weight(self):
    #     for line in self:
    #         # Ensure fine weight updates if fineness changes manually
    #         line.fine_weight = line.fineness * line.net_weight

    @api.depends('bom_id', 'product_uom_qty')
    def _compute_cost(self):
        for line in self:
            if line.bom_id:
                total_cost_per_unit = 0.0

                for bom_line in line.bom_id.bom_line_ids:
                    component_product = bom_line.product_id
                    component_qty = bom_line.product_qty

                    component_cost = component_qty * component_product.standard_price
                    total_cost_per_unit += component_cost

                line.cost = total_cost_per_unit * line.product_uom_qty
            else:
                line.cost = 0.0

    # @api.depends('fine_weight', 'wastage_percent')
    # def _compute_wastage_weight_fine(self):
    #     for line in self:
    #         if line.fine_weight and line.wastage_percent:
    #             line.wastage_weight_fine = line.fine_weight - (line.fine_weight * line.wastage_percent / 100)
    #         else:
    #             line.wastage_weight_fine = 0.0


    @api.onchange('product_id')
    def _onchange_product_id_set_wastage(self):
        if self.product_id:
            self.wastage_percent = self.product_id.product_tmpl_id.wastage_percent


    @api.depends('net_weight', 'fineness', 'wastage_percent')
    def _compute_fine_weight(self):
        for line in self:
            line.fine_weight = (
                    (line.net_weight or 0.0) *
                    (line.fineness or 0.0) *
                    (1 - (line.wastage_percent or 0.0) / 100)  )

