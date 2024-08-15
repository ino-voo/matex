# -*- coding: utf-8 -*-
import xmlrpc.client
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def send_and_create_purchase_order(self):
        # Odoo credentials
        url = 'https://grupobibo.odoo.com'
        db = 'grupobibo-15-0-5869337'
        username = 'procesos@bibo.com.mx'
        password = 'Hol@mund0'
        # url = 'http://localhost:8067'
        # db = 'matex.test'
        # username = 'admin'
        # password = 'sist3mas'
        # Common endpoint
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        # Authenticate
        uid = common.authenticate(db, username, password, {})
        # Object endpoint
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        if self.partner_id.vat != 'SPS0904307J9':
            raise UserError(_('El partner debe tener el RFC %s') % 'SPS0904307J9')

        purchase_order_id = self
        purchase_partner = self.company_id
        purchase_order_lines = self.env['purchase.order.line'].search([('order_id', '=', purchase_order_id.id)])

        if not purchase_order_lines:
            raise UserError(_('No purchase order lines found'))

        # Prepare the sale order line data from the purchase order lines
        sale_order_lines = []
        for line in purchase_order_lines:

            text = line.name
            start = text.find('[') + 1
            end = text.find(']')
            product_code = text[start:end]

            product = models.execute_kw(db, uid, password, 'product.product', 'search_read',
                                        [[['default_code', '=', product_code]]])
            if not product:
                raise UserError(_('No se encotro el codigo de producto %s') % product_code)

            sale_order_lines.append((0, 0, {
                'product_id': product[0]['id'],
                'product_uom_qty': line.product_qty,
            }))

        # Search and create the partner
        partner = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
                                    [[['vat', '=', purchase_partner.vat]]])                
        if not partner:
            raise UserError(_('No se encontró el partner con el RFC %s') % partner.vat)
        partner_id = partner[0]['id']

        # Create the sale order
        sale_order_id = models.execute_kw(db, uid, password, 'sale.order', 'create', [{
            'partner_id': partner_id,
            'client_order_ref': purchase_order_id.name,
            'partner_invoice_id': partner_id,
            'order_line': sale_order_lines,
        }])
        # Search and post the sale order
        sale = models.execute_kw(db, uid, password, 'sale.order', 'search_read', [[[
            'id', '=', sale_order_id]]])
        self.write({'partner_ref': sale[0]['name']})
        self.message_post(body=_('Se ha creado la orden de venta %s') % sale[0]['name'])
