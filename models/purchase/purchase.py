# -*- coding: utf-8 -*-

from odoo import api, fields, models

import xmlrpc.client


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # product_id = fields.Many2one('product.product', string='Product', compute='_compute_product_id')

    # @api.multi
    # def _compute_product_id(self):
    #     for order in self:
    #         order.product_id = order.order_line.product_id

    def send_and_create_purchase_order(self):



        # Odoo credentials
        url = 'https://grupobibo.odoo.com'
        db = 'grupobibo-15-0-5869337'
        username = 'procesos@bibo.com.mx'
        password = 'Hol@mund0'

        # Common endpoint
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))

        # Authenticate
        uid = common.authenticate(db, username, password, {})

        if uid:
            print("Authenticated successfully")
        else:
            print("Authentication failed")
            exit()

        # Object endpoint
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        
        # Example: Search for records
        records = models.execute_kw(db, uid, password, 'purchase.order', 'search', 
            [[['id', '=', 157916]], {'company_id': 1}])

        print(records)


