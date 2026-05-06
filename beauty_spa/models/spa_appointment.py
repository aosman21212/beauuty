from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SpaAppointment(models.Model):
    _name = 'spa.appointment'
    _description = 'Spa Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'appointment_date desc, name desc'

    # ── Identity ──────────────────────────────────────────────────────────────
    name = fields.Char(
        string='Reference', required=True, copy=False, readonly=True,
        default='New',
    )
    client_id = fields.Many2one(
        'res.partner', string='Client', required=True, tracking=True,
        index=True,
    )
    therapist_id = fields.Many2one(
        'spa.therapist', string='Therapist', required=True, tracking=True,
        index=True,
    )
    room_id = fields.Many2one('spa.room', string='Room', tracking=True)
    color = fields.Integer(related='therapist_id.color', store=True)

    # ── Schedule ──────────────────────────────────────────────────────────────
    appointment_date = fields.Datetime(
        string='Start', required=True, tracking=True,
        default=fields.Datetime.now,
    )
    duration = fields.Float(
        string='Duration (min)', compute='_compute_duration',
        store=True, readonly=False,
    )
    appointment_end = fields.Datetime(
        string='End', compute='_compute_appointment_end', store=True,
    )

    # ── Services / Package ────────────────────────────────────────────────────
    service_ids = fields.Many2many(
        'spa.service',
        'spa_appointment_service_rel',
        'appointment_id',
        'service_id',
        string='Services',
    )
    package_id = fields.Many2one('spa.package', string='Package')

    # ── Financials ────────────────────────────────────────────────────────────
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    total_price = fields.Monetary(
        string='Total', currency_field='currency_id',
        compute='_compute_total_price', store=True,
    )
    invoice_id = fields.Many2one(
        'account.move', string='Invoice', copy=False, readonly=True,
    )
    invoice_state = fields.Selection(
        related='invoice_id.payment_state', string='Payment', store=True,
    )

    # ── Status ────────────────────────────────────────────────────────────────
    state = fields.Selection([
        ('draft', 'New'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, index=True)

    notes = fields.Text(string='Internal Notes')

    # ── Computed ──────────────────────────────────────────────────────────────
    @api.depends('service_ids', 'package_id')
    def _compute_duration(self):
        for rec in self:
            if rec.package_id:
                rec.duration = rec.package_id.total_duration
            elif rec.service_ids:
                rec.duration = sum(rec.service_ids.mapped('duration'))
            else:
                rec.duration = 60.0

    @api.depends('appointment_date', 'duration')
    def _compute_appointment_end(self):
        for rec in self:
            if rec.appointment_date and rec.duration:
                from datetime import timedelta
                rec.appointment_end = rec.appointment_date + timedelta(
                    minutes=rec.duration
                )
            else:
                rec.appointment_end = rec.appointment_date

    @api.depends('service_ids.price', 'package_id.package_price')
    def _compute_total_price(self):
        for rec in self:
            if rec.package_id:
                rec.total_price = rec.package_id.package_price
            elif rec.service_ids:
                rec.total_price = sum(rec.service_ids.mapped('price'))
            else:
                rec.total_price = 0.0

    # ── Sequence ──────────────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'spa.appointment'
                ) or 'New'
        return super().create(vals_list)

    # ── Constraints ───────────────────────────────────────────────────────────
    @api.constrains('appointment_date', 'appointment_end', 'therapist_id')
    def _check_therapist_overlap(self):
        for rec in self:
            if not rec.appointment_date or not rec.appointment_end:
                continue
            overlap = self.search([
                ('id', '!=', rec.id),
                ('therapist_id', '=', rec.therapist_id.id),
                ('state', 'not in', ['cancelled']),
                ('appointment_date', '<', rec.appointment_end),
                ('appointment_end', '>', rec.appointment_date),
            ])
            if overlap:
                raise ValidationError(_(
                    'Therapist %(therapist)s already has appointment %(apt)s '
                    'during this time slot.',
                    therapist=rec.therapist_id.name,
                    apt=overlap[0].name,
                ))

    # ── State transitions ─────────────────────────────────────────────────────
    def action_confirm(self):
        self.filtered(lambda r: r.state == 'draft').write({'state': 'confirmed'})

    def action_start(self):
        self.filtered(lambda r: r.state == 'confirmed').write({'state': 'in_progress'})

    def action_done(self):
        self.filtered(lambda r: r.state == 'in_progress').write({'state': 'done'})

    def action_cancel(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_('Cannot cancel a completed appointment.'))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.filtered(lambda r: r.state == 'cancelled').write({'state': 'draft'})

    # ── Invoice ───────────────────────────────────────────────────────────────
    def action_create_invoice(self):
        self.ensure_one()
        if self.invoice_id:
            return self._open_invoice()
        if self.state not in ('confirmed', 'in_progress', 'done'):
            raise UserError(_('Please confirm the appointment before invoicing.'))

        lines = []
        if self.package_id:
            lines.append((0, 0, {
                'name': self.package_id.name,
                'quantity': 1,
                'price_unit': self.package_id.package_price,
            }))
        else:
            for svc in self.service_ids:
                lines.append((0, 0, {
                    'name': svc.name,
                    'quantity': 1,
                    'price_unit': svc.price,
                    'product_id': svc.product_id.id if svc.product_id else False,
                }))

        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.client_id.id,
            'invoice_line_ids': lines,
            'narration': f'Appointment {self.name} on '
                         f'{self.appointment_date.strftime("%Y-%m-%d %H:%M")}',
        })
        self.invoice_id = move
        return self._open_invoice()

    def _open_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoice'),
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
        }

    def action_view_invoice(self):
        self.ensure_one()
        if not self.invoice_id:
            raise UserError(_('No invoice found for this appointment.'))
        return self._open_invoice()
