from odoo import models, fields, api
from odoo.exceptions import UserError

class CreateMoWizard(models.TransientModel):
    _name = 'create.mo.wizard'
    _description = 'Create Manufacturing Order Wizard'

    sale_order_report_id = fields.Many2one('sale.order.report', string='Sale Order Report', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    bom_id = fields.Many2one('mrp.bom', string='BOM', readonly=True)
    process_bom_id = fields.Many2one('mrp.bom', string='Process BOM', readonly=True)
    mo_quantity = fields.Float(string='Manufacturing Quantity', required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        report = self.env['sale.order.report'].browse(self.env.context.get('active_id'))

        mo_list = self.env['mrp.production'].search([
            ('origin', '=', report.order_id.name),
            ('product_id', '=', report.product_id.id),
            ('state', 'not in', ['cancel'])
        ])
        manufactured_qty = sum(mo.product_qty for mo in mo_list)
        remaining_qty = report.product_uom_qty - manufactured_qty

        res.update({
            'sale_order_report_id': report.id,
            'product_id': report.product_id.id,
            'bom_id': report.bom_id.id,
            'process_bom_id': report.process_bom_id.id,
            'mo_quantity': remaining_qty,
        })
        return res

    def create_mo(self):
        self.ensure_one()
        if self.mo_quantity <= 0:
            raise UserError("Manufacturing quantity must be greater than zero.")

        report = self.sale_order_report_id
        mo_list = self.env['mrp.production'].search([
            ('origin', '=', report.order_id.name),
            ('product_id', '=', report.product_id.id),
            ('state', 'not in', ['cancel'])
        ])
        manufactured_qty = sum(mo.product_qty for mo in mo_list)
        remaining_qty = report.product_uom_qty - manufactured_qty

        if self.mo_quantity > remaining_qty:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Confirm Overproduction',
                'res_model': 'confirm.mo.overproduce',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_wizard_id': self.id,
                    'default_warning_message': f"You are trying to manufacture {self.mo_quantity}, "
                                               f"which is more than the remaining demand ({remaining_qty}). Proceed?"
                }
            }

        return self._create_mo_record()

    def _create_mo_record(self):
        mo = self.env['mrp.production'].create({
            'product_id': self.product_id.id,
            'product_qty': self.mo_quantity,
            'bom_id': self.process_bom_id.id,
            'origin': self.sale_order_report_id.order_id.name,
        })

        mo.action_confirm()

        # Open Add Stone Wizard and pass MO ID
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Stone Components',
            'res_model': 'add.stone.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_mo_id': mo.id,
                'default_sale_order_report_id': self.sale_order_report_id.id,
                'default_bom_id': self.bom_id.id,
                'default_mo_quantity': self.mo_quantity
            }
        }


class ConfirmMoOverproduce(models.TransientModel):
    _name = 'confirm.mo.overproduce'
    _description = 'Confirm Overproduction Warning'

    wizard_id = fields.Many2one('create.mo.wizard', string="MO Wizard", required=True)
    warning_message = fields.Text(string="Warning", readonly=True)

    def confirm_overproduce(self):
        return self.wizard_id.create_mo()






class AddStoneWizard(models.TransientModel):
    _name = 'add.stone.wizard'
    _description = 'Add Stone Wizard'

    mo_id = fields.Many2one('mrp.production', string='Manufacturing Order', readonly=True)
    sale_order_report_id = fields.Many2one('sale.order.report', string='Sale Order Report', readonly=True)
    bom_id = fields.Many2one('mrp.bom', string='BOM', readonly=True)
    mo_quantity = fields.Float(string='Manufacturing Quantity', readonly=True)

    def add_stones(self):
        self.ensure_one()

        # Start from the parent MO (product A)
        parent_mo = self.mo_id

        if not parent_mo:
            raise UserError("Parent Manufacturing Order not found.")

        # Search all child MOs related to this parent MO
        child_mos = self.env['mrp.production'].search([('origin', '=', parent_mo.name)])

        if not child_mos:
            raise UserError("No child Manufacturing Orders found for this MO.")

        # Find the MO where has_setting is True
        setting_mo = child_mos.filtered(lambda mo: mo.has_setting)

        if not setting_mo:
            raise UserError("No child Manufacturing Order with a setting product found.")

        setting_mo = setting_mo[0]  # Get the first matching MO

        # Add stone components to the found MO
        for line in self.bom_id.bom_line_ids:
            if line.product_id.component_type == 'stone':
                self.env['stock.move'].create({
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': (line.product_qty * self.mo_quantity) / self.bom_id.product_qty,
                    'product_uom': line.product_uom_id.id,
                    'raw_material_production_id': setting_mo.id,
                    'location_id': setting_mo.location_src_id.id,
                    'location_dest_id': setting_mo.location_dest_id.id,
                })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'res_id': setting_mo.id,
            'view_mode': 'form',
            'target': 'current',
        }
