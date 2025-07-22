from odoo import models, fields

class SizeMaster(models.Model):
    _name = "size.master"
    _description = "Size Master"
    _rec_name = "size"

    size = fields.Char(string="Size", required=True)
