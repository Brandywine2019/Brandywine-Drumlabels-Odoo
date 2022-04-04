from odoo import fields, models, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    hide_reconcile = fields.Boolean(compute="_compute_hide_reconcile")

    def _compute_hide_reconcile(self):
        action = self.env.ref('account_accountant.action_view_account_move_line_reconcile')
        if self.env.context.get('hide_reconcile'):
            action.create_action()
        else:
            action.unlink_action()
        for line in self:
            if self.env.context.get('hide_reconcile'):
                line.hide_reconcile = True
            else:
                line.hide_reconcile = False


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    def open_journal_items(self, options, params):
        action = super(AccountReport, self).open_journal_items(options, params)
        action['domain'].append(('account_id','=',int(action['context'].get('active_id'))))
        return action