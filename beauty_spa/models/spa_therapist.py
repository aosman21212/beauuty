from odoo import api, fields, models


class SpaTherapist(models.Model):
    _name = 'spa.therapist'
    _description = 'Spa Therapist'
    _order = 'name'

    name = fields.Char(string='Therapist Name', required=True)
    image = fields.Image(max_width=256, max_height=256)
    job_title = fields.Char(string='Specialisation')
    phone = fields.Char()
    email = fields.Char()
    color = fields.Integer(string='Colour Index', default=0)
    service_ids = fields.Many2many(
        'spa.service',
        'spa_therapist_service_rel',
        'therapist_id',
        'service_id',
        string='Offered Services',
    )
    active = fields.Boolean(default=True)
    appointment_count = fields.Integer(
        string='Appointments',
        compute='_compute_appointment_count',
    )

    def _compute_appointment_count(self):
        data = self.env['spa.appointment'].read_group(
            [('therapist_id', 'in', self.ids)],
            ['therapist_id'],
            ['therapist_id'],
        )
        mapped = {d['therapist_id'][0]: d['therapist_id_count'] for d in data}
        for rec in self:
            rec.appointment_count = mapped.get(rec.id, 0)

    def action_view_appointments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} — Appointments',
            'res_model': 'spa.appointment',
            'view_mode': 'calendar,list,form',
            'domain': [('therapist_id', '=', self.id)],
            'context': {'default_therapist_id': self.id},
        }
