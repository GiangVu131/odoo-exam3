from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    plan_sale_order = fields.Many2one('plan.sale.order', string='Orders',
                                      ondelete='cascade', index=True, copy=False,
                                      invisible=True)

    pso = fields.One2many('plan.sale.order', 'quotations', string='Order')
    quotations_re = fields.Many2one(related='pso.quotations', string='test')
    state_re = fields.Selection(related='pso.state', string='test 2')

    # def btn_create_plan(self):
    #     return {
    #         'name': 'Create plan sale order',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'plan.sale.order',
    #         'target': 'new',
    #     }

    # Nút nhấn confirm
    def _action_confirm(self):
        for order in self:
            if any(expense_policy not in [False, 'no'] for expense_policy in
                   order.order_line.mapped('product_id.expense_policy')):
                if not order.analytic_account_id:
                    order._create_analytic_account()
        return True

    def action_done(self):
        for order in self:
            tx = order.sudo().transaction_ids._get_last()
            if tx and tx.state == 'pending' and tx.acquirer_id.provider == 'transfer':
                tx._set_done()
                tx.write({'is_post_processed': True})
        return self.write({'state': 'done'})

    def _prepare_confirmation_values(self):
        return {
            'state': 'sale',
            'date_order': fields.Datetime.now()
        }

    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))
        # Code them vao
        if not self.quotations_re or self.state_re != 'approve':
            raise models.ValidationError('Not available/Not approved plan sale order')

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write(self._prepare_confirmation_values())
        context = self._context.copy()
        context.pop('default_name', None)
        self.with_context(context)._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        return True

    def _get_forbidden_state_confirm(self):
        return {'done', 'cancel'}

