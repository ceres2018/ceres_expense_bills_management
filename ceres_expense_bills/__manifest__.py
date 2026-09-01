# -*- coding: utf-8 -*-
{
    'name': 'Ceres Expense Bills Management',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Expenses',
    'summary': 'Odoo 18 Community: separate expense bills from vendor bills',
    'description': """
Ceres Expense Bills Management
==============================

Odoo 18 Community Edition addon. Also compatible with Odoo 18 Enterprise.

Separates accounting records generated from Expense Reports from normal
supplier vendor bills. Uses only standard Community dependencies
(hr_expense, account). No Enterprise-only modules required.

* Expense bills: Expenses > Expense Bills
* Vendor bills: Accounting > Vendors > Bills
* Posting, payments, and reconciliation remain standard Odoo
    """,
    'author': 'Ceres - IT Solution',
    'maintainer': 'Ceres - IT Solution',
    'website': 'https://www.ceresitsolution.com/',
    'support': 'info@ceresitsolution.com',
    'depends': ['hr_expense', 'account'],
    'data': [
        'views/expense_bill_views.xml',
        'views/account_move_views.xml',
        'views/menu.xml',
    ],
    'images': [
        'static/description/icon.png',
        'static/description/screenshots/expense_bills_menu.png',
        'static/description/screenshots/expense_bills_list.png',
        'static/description/screenshots/expense_bill_form.png',
        'static/description/screenshots/expense_bills_filters.png',
        'static/description/screenshots/expense_bills_groupby.png',
        'static/description/screenshots/vendor_bills_separation.png',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
