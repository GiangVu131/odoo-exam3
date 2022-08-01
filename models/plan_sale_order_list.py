from odoo import fields, models, api


class PlanSaleOrderList(models.Model):
    _name = 'plan.sale.order.list'
    _description = 'Description'

    approval_person = fields.Many2one('res.partner', string='Approval Person')
    status_approval = fields.Selection([
        ('not_available', 'Not available'),
        ('approved', 'Approved'),
        ('denied', 'Denied')],
        string='Status', default='not_available', )

    order_id = fields.Many2one('plan.sale.order', string='Order Reference',
                               ondelete='cascade', index=True, copy=False,
                               invisible=True)
    state_re = fields.Selection(related='order_id.state', string='test')

    def btn_approve(self):
        self.status_approval = 'approved'
        data = self.order_id.order_line.mapped('status_approval')
        if all([state == 'approved' for state in data]):
            self.order_id.new_check = 'yes'

    def btn_denied(self):
        self.status_approval = 'denied'
        if self.status_approval == 'denied':
            self.order_id.state = 'deny'

        # is_order_approved = False
        # if self.order_id:
        #     if len(self.order_id.order_line) > 0:
        #         for line in self.order_id.order_line:
        #             if line.status_approval == 'approved':
        #                 is_order_approved = False
        #             else:
        #                 is_order_approved = True
        # if is_order_approved is False:
        #     self.order_id.state = 'approve'
