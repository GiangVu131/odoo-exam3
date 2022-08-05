from odoo import api, fields, models, tools, _
from odoo.http import request, route


class PlanSaleOrder(models.Model):
    _name = 'plan.sale.order'
    _inherit = ['mail.thread']
    name = fields.Text('Name', required=True, store=True)
    quotations = fields.Many2one('sale.order', string='Quotations', store=True)
    info_plan_sale_order = fields.Text(required=True, string='info')
    state = fields.Selection([
        ('new', 'New'),
        ('send', 'Send'),
        ('approve', 'Approve'),
        ('deny', 'Deny'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='new')
    order_line = fields.One2many('plan.sale.order.list', 'order_id', string='Order Lines',
                                 states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, )
    create_uid = fields.Many2one('res.users', string='')

    new_check = fields.Selection([('yes', 'Yes'), ('no', 'No')])

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [
            ('new', 'send'),
            ('send', 'new'),
            ('send', 'deny'),
            ('deny', 'new'),
            ('send', 'approve'),
            ('approve', 'new'),
        ]
        return (old_state, new_state) in allowed

    def change_state(self, new_state):
        for r in self:
            if r.is_allowed_transition(r.state, new_state):
                r.state = new_state
            else:
                continue

    def btn_new(self):
        self.change_state('new')
        if self.state == 'new':
            self.order_line.status_approval = 'not_available'
            self.new_check = ''

    def btn_send(self):
        for rec in self:
            if not rec.order_line.approval_person:
                raise models.ValidationError('No one approve')
            else:
                rec.change_state('send')
                rec.sudo().message_post(body=_(("<b> <h2> New plan sale order avalible </h2> </b>")),
                                        partner_ids=rec.order_line.approval_person.ids,
                                        message_type='notification')

    def btn_confirm(self):
        if self.new_check == 'yes':
            self.state = 'approve'
            self.sudo().message_post(body=_(("<b> <h2> Your plan sale order is approved </h2> </b>")),
                                     partner_ids=self.create_uid.partner_id.ids,
                                     message_type='notification')
