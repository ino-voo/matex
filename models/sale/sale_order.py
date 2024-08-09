# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    qty_pieces = fields.Integer(string='Cantidad de piezas', compute='_compute_qty_pieces')

    @api.depends('order_line.product_uom_qty')
    def _compute_qty_pieces(self):
        for order in self:
            qty_pieces = 0
            for line in order.order_line.filtered(lambda x: x.product_type == 'product'):
                qty_pieces += line.product_uom_qty
            order.qty_pieces = qty_pieces
