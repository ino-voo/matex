# -*- coding: utf-8 -*-
import xmlrpc.client
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    api_send = fields.Boolean(string='Enviar a Bibo', default=False)

    def send_and_create_purchase_order(self):
        # Odoo credentials
        url = 'https://grupobibo.odoo.com'
        db = 'grupobibo-15-0-5869337'
        username = 'procesos@bibo.com.mx'
        password = '566af3f93b7692f1e728bc924105d55b270b155d'

        # Common endpoint
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))

        # Authenticate
        uid = common.authenticate(db, username, password, {})

        # Object endpoint
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        # Optionally ensure the user is set to the correct company
        models.execute_kw(db, uid, password, 'res.users', 'write', [[uid], {'company_id': 1}])

        # Validate partner's VAT
        if self.partner_id.vat != 'SPS0904307J9':
            raise UserError(_('El partner debe tener el RFC %s') % 'SPS0904307J9')

        purchase_order_id = self
        
        sales = purchase_order_id._get_sale_orders()
        sale_origin = sales.client_order_ref

        purchase_partner = self.company_id

        purchase_order_lines = self.env['purchase.order.line'].search([('order_id', '=', purchase_order_id.id)])

        if not purchase_order_lines:
            raise UserError(_('No purchase order lines found'))

        _logger.info('Purchase order lines: %s' % purchase_order_lines)
        # Prepare the sale order line data from the purchase order lines
        sale_order_lines = []
        for line in purchase_order_lines:
            text = line.name
            start = text.find('[') + 1
            end = text.find(']')
            product_code = text[start:end]

            _logger.info('product_code: %s' % product_code)
            # Search for the product with company_id filter
            product = models.execute_kw(db, uid, password, 'product.product', 'search_read',
                                        [[['default_code', '=', product_code], ['company_id', '=', 1]]],
                                        {'fields': ['id']})

            _logger.info('Product: %s' % product)

            if not product:
                raise UserError(_('No se encontró el código de producto %s') % product_code)

            sale_order_lines.append((0, 0, {
                'product_id': product[0]['id'],
                'product_uom_qty': line.product_qty,
            }))

        _logger.info('Sale order lines: %s' % sale_order_lines)
        # Search for the partner with company_id filter
        partner = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
                                    [[['vat', '=', purchase_partner.vat], ['company_id', '=', 1]]],
                                    {'fields': ['id']})

        _logger.info('Partner: %s' % partner)

        if not partner:
            raise UserError(_('No se encontró el partner con el RFC %s') % purchase_partner.vat)

        partner_id = partner[0]['id']
        # Create the sale order
        sale_order_id = models.execute_kw(db, uid, password, 'sale.order', 'create', [{
            'partner_id': partner_id,
            'client_order_ref': sale_origin,
            'partner_invoice_id': partner_id,
            'order_line': sale_order_lines,
            'company_id': 1  # Ensuring the sale order is created for the correct company
        }])

        _logger.info('Sale order: %s' % sale_order_id)
        # Search and post the sale order
        sale = models.execute_kw(db, uid, password, 'sale.order', 'search_read', 
                                [[['id', '=', sale_order_id], ['company_id', '=', 1]]])

        _logger.info('Sale: %s' % sale)
        

        template = self.env.ref('purchase.email_template_edi_purchase', raise_if_not_found=False)
        if template:
            orders = self
            for order in orders:
                order.with_context(is_reminder=True).message_post_with_source(
                    template,
                    email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature",
                    subtype_xmlid='mail.mt_comment')

        self.write({'partner_ref': sale[0]['name'], 'api_send': True})
        self.message_post(body=_('Se ha creado la orden de venta %s') % sale[0]['name'])
