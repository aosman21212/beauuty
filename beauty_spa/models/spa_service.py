from odoo import api, fields, models


class SpaService(models.Model):
    _name = 'spa.service'
    _description = 'Spa Service'
    _order = 'category_id, sequence, name'

    name = fields.Char(string='Service Name', required=True, translate=True)
    sequence = fields.Integer(default=10)
    category_id = fields.Many2one(
        'spa.service.category', string='Category', ondelete='set null', index=True,
    )
    description = fields.Html(translate=True)
    duration = fields.Float(string='Duration (min)', required=True, default=60.0)
    price = fields.Monetary(string='Price', currency_field='currency_id', required=True)
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    active = fields.Boolean(default=True)
    product_id = fields.Many2one(
        'product.product',
        string='Invoiceable Product',
        domain=[('type', '=', 'service')],
        help='Linked product used when generating invoices.',
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price = self.product_id.lst_price
            if not self.name:
                self.name = self.product_id.name
