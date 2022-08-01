from odoo import fields, models, api


class PopupPlanSaleOrder(models.TransientModel):
    _name = 'popup.plan.sale.order'
    _description = 'Description'

    name = fields.Char()
    plan_sale_order = fields.Many2one(
        comodel_name='plan.sale.order',
        string='Plan_sale_order',
        required=False)
    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale_order',
        required=False)

    def confirm_plan_sale_order(self):
        for rec in self:
            if rec.sale_order_id:
                vals = {
                    'state': 'approve',
                }
                plan_sale_order = self.env['plan.sale.order']
                plan_sale_order.create(vals)
