
from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    gross_weight = fields.Float(string="Gross Weight (kg)", digits=(16, 3))
    net_weight = fields.Float(string="Net Weight (kg)", digits=(16, 3))

    @api.model
    def create(self, vals):
        mo = super().create(vals)
        if not vals.get('gross_weight'):
            mo._set_default_gross_weight()
        mo._cascade_weights_and_quantities()
        return mo

    def action_confirm(self):
        res = super().action_confirm()
        for mo in self:
            mo._cascade_weights_and_quantities()
        return res

    def _set_default_gross_weight(self):
        for mo in self:
            product_gross = mo.product_id.product_tmpl_id.gross_weight or 0.0
            mo.write({
                'gross_weight': product_gross,
                'net_weight': product_gross,
            })

    def _cascade_weights_and_quantities(self):
        """
        Apply weights and compute quantities down the MO hierarchy.
        """

        def recurse(mo, incoming_weight, is_main_mo):
            if not mo:
                return

            mo_weight = incoming_weight

            # Main MO keeps user-defined quantity
            if not is_main_mo:
                mo.write({
                    'product_qty': mo_weight,
                })

            mo.write({
                'gross_weight': mo_weight,
                'net_weight': mo_weight,
            })

            # Calculate stone weight from BOM components (stone type fetched from product)
            stone_weight = 0.0
            for line in mo.bom_id.bom_line_ids:
                product_type = line.product_id.product_tmpl_id.component_type
                if product_type == 'stone':
                    stone_weight += line.product_qty

            wip_weight = max(mo_weight - stone_weight, 0.0)

            # Update component move quantities
            for move in mo.move_raw_ids:
                bom_line = mo.bom_id.bom_line_ids.filtered(lambda l: l.product_id == move.product_id)
                if not bom_line:
                    continue

                product_type = move.product_id.product_tmpl_id.component_type

                if product_type == 'stone':
                    move.product_uom_qty = bom_line[0].product_qty
                elif product_type == 'wip':
                    move.product_uom_qty = wip_weight
                else:
                    move.product_uom_qty = mo_weight

            # Recursively apply to child MOs
            child_mos = self.env['mrp.production'].search([
                ('origin', '=', mo.name),
                ('id', '!=', mo.id),
            ])
            for child in child_mos:
                recurse(child, wip_weight, is_main_mo=False)

        for mo in self:
            if mo.gross_weight:
                recurse(mo, mo.gross_weight, is_main_mo=True)
