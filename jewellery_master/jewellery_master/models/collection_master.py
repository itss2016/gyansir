from odoo import models, fields, api

class CollectionMaster(models.Model):
    _name = "collection.master"
    _description = "Collection Master"
    _rec_name = "collection_master"

    collection_master = fields.Char(string="Collection Master", required=True)
   
    