from odoo import models, fields

class MetalMaster(models.Model):
    _name = "metal.master"
    _description = "Metal Master"

    name = fields.Char(string="Metal", required=True)  # Metal Name
    fineness_ids = fields.One2many("metal.fineness", "metal_id", string="Fineness Levels")


class MetalFineness(models.Model):
    _name = "metal.fineness"
    _description = "Metal Fineness"

    metal_id = fields.Many2one("metal.master", string="Metal", required=True, ondelete="cascade")
    fineness = fields.Float(string="Fineness", digits=(16, 4))
