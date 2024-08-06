# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for move in self:
            for line in move.invoice_line_ids:
                if line.quantity == 0:
                    raise UserError(_('No es posible generar facturas con cantidad 0!'))
        return res

