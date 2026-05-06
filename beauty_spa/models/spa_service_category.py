from odoo import fields, models


class SpaServiceCategory(models.Model):
    _name = 'spa.service.category'
    _description = 'Spa Service Category'
    _order = 'sequence, name'

    name = fields.Char(string='Category', required=True, translate=True)
    sequence = fields.Integer(default=10)
    description = fields.Text(translate=True)
    color = fields.Integer(string='Colour Index', default=0)
    service_count = fields.Integer(
        string='Services',
        compute='_compute_service_count',
    )

    def _compute_service_count(self):
        data = self.env['spa.service'].read_group(
            [('category_id', 'in', self.ids)],
            ['category_id'],
            ['category_id'],
        )
        mapped = {d['category_id'][0]: d['category_id_count'] for d in data}
        for rec in self:
            rec.service_count = mapped.get(rec.id, 0)

    def action_view_services(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} — Services',
            'res_model': 'spa.service',
            'view_mode': 'list,form',
            'domain': [('category_id', '=', self.id)],
            'context': {'default_category_id': self.id},
        }
