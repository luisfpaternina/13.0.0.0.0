# -*- coding: utf-8 -*-
{
    'name': 'Partner Ledger Open Items',
    'version': '1.0',
    'description': 'This module create Partner Ledger report to reconcile accounts',
    'author': 'Syscoon',
    'website': '',
    'license': 'LGPL-3',
    'category': 'Account',
    'depends': [
        'account_reports',
    ],
    'data': [
        "security/ir.model.access.csv",
        "data/partner_ledger_open_items_view.xml"
    ],
    'auto_install': False,
    'application': True,
}