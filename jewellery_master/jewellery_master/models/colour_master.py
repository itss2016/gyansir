from odoo import models, fields

class ColourMaster(models.Model):
    _name = "colour.master"
    _description = "Colour Master"
    _rec_name = "colour"

    colour = fields.Char(string="Color", required=True)
