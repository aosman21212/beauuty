from odoo import fields, models


class SpaRoom(models.Model):
    _name = 'spa.room'
    _description = 'Spa Treatment Room'
    _order = 'name'

    name = fields.Char(string='Room Name', required=True)
    capacity = fields.Integer(string='Capacity', default=1)
    description = fields.Text()
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Colour Index', default=0)
