from odoo import api, fields, models


class SpaPackage(models.Model):
    _name = 'spa.package'
    _description = 'Spa Treatment Package'
    _order = 'name'

    name = fields.Char(string='Package Name', required=True, translate=True)
    description = fields.Html(translate=True)
    line_ids = fields.One2many('spa.package.line', 'package_id', string='Services')
    total_duration = fields.Float(
        string='Total Duration (min)', compute='_compute_totals', store=True,
    )
    list_price = fields.Monetary(
        string='Normal Price', compute='_compute_totals', store=True,
        currency_field='currency_id',
    )
    package_price = fields.Monetary(
        string='Package Price', currency_field='currency_id', required=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    savings = fields.Monetary(
        string='Savings', compute='_compute_totals', store=True,
        currency_field='currency_id',
    )
    active = fields.Boolean(default=True)

    @api.depends('line_ids.service_id', 'line_ids.quantity', 'package_price')
    def _compute_totals(self):
        for rec in self:
            duration = 0.0
            price = 0.0
            for line in rec.line_ids:
                if line.service_id:
                    duration += line.service_id.duration * line.quantity
                    price += line.service_id.price * line.quantity
            rec.total_duration = duration
            rec.list_price = price
            rec.savings = price - rec.package_price


class SpaPackageLine(models.Model):
    _name = 'spa.package.line'
    _description = 'Spa Package Line'
    _order = 'sequence, id'

    package_id = fields.Many2one('spa.package', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    service_id = fields.Many2one('spa.service', required=True, string='Service')
    quantity = fields.Integer(string='Qty', default=1)
    subtotal = fields.Monetary(
        string='Subtotal', compute='_compute_subtotal', store=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        related='package_id.currency_id', store=True,
    )

    @api.depends('service_id.price', 'quantity')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = (line.service_id.price or 0.0) * line.quantity
