# -*- coding: utf-8 -*-
{
    "name": "Matex",
    "version": "17.0.0.0.1",
    "summary": "Matex Customization",
    "depends": [
        "account",
        "l10n_mx_edi",
        "purchase",
        "sale",
        "sale_margin",
    ],
    "data": [
        "report/report_invoice_templates.xml",
        "report/report_payment_receipt_templates.xml",
        "report/report_saleorder_templates.xml",
        "views/purchase_views.xml",
        "views/sale_order_views.xml",
        ],
    "installable": True,
    "license": "AGPL-3",
}
