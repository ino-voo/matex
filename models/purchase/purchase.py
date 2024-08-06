# -*- coding: utf-8 -*-

from odoo import api, fields, models

import xmlrpc.client


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


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

        # models.execute_kw(db, uid, password, 'res.users', 'write',
        #                         [[54], {'company_id': 1}])

        sales = models.execute_kw(db, uid, password, 'sale.order', 'search_read',
                                            [[['id', '=', 157916]]])

        # records = models.execute_kw(db, uid, password, 'purchase.order', 'search', 
        #     [[['id', '=', 157916]], {'company_id': 1}])

        print('purchases', sales)


