# -*- coding: utf-8 -*-
from odoo import Command
from odoo.tests import tagged

from odoo.addons.hr_expense.tests.common import TestExpenseCommon


@tagged('post_install', '-at_install', 'ceres_expense_bills_management')
class TestCeresExpenseBillsManagement(TestExpenseCommon):

    def _vendor_bills_domain(self):
        return self.env.ref('account.action_move_in_invoice_type').domain

    def _expense_bills_domain(self):
        return self.env.ref('ceres_expense_bills_management.action_expense_bills').domain

    def _post_expense_report(self, sheet):
        sheet._do_submit()
        sheet._do_approve()
        sheet.action_sheet_move_post()

    def test_vendor_bill_not_in_expense_bills(self):
        """Manually created vendor bills stay in Vendor Bills, not Expense Bills."""
        vendor_bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.partner_a.id,
            'invoice_date': '2022-01-25',
            'invoice_line_ids': [Command.create({
                'name': 'Supplier service',
                'product_id': self.product_a.id,
                'quantity': 1,
                'price_unit': 500.0,
            })],
        })
        self.assertFalse(vendor_bill.is_expense_bill)
        vendor_moves = self.env['account.move'].search(self._vendor_bills_domain())
        expense_moves = self.env['account.move'].search(self._expense_bills_domain())
        self.assertIn(vendor_bill, vendor_moves)
        self.assertNotIn(vendor_bill, expense_moves)

    def test_expense_bill_separation(self):
        """Posted expense reports create expense bills excluded from Vendor Bills."""
        sheet = self.create_expense_report({
            'expense_line_ids': [
                Command.create({
                    'employee_id': self.expense_employee.id,
                    'product_id': self.product_a.id,
                    'total_amount_currency': 100.0,
                    'payment_mode': 'own_account',
                    'company_id': self.company_data['company'].id,
                    'date': self.frozen_today,
                }),
                Command.create({
                    'employee_id': self.expense_employee.id,
                    'product_id': self.product_b.id,
                    'total_amount_currency': 200.0,
                    'payment_mode': 'own_account',
                    'company_id': self.company_data['company'].id,
                    'date': self.frozen_today,
                }),
            ],
        })
        self._post_expense_report(sheet)
        move = sheet.account_move_ids
        self.assertEqual(len(move), 1)
        self.assertTrue(move.is_expense_bill)
        self.assertEqual(set(move.expense_category_ids.ids), {self.product_a.id, self.product_b.id})
        vendor_moves = self.env['account.move'].search(self._vendor_bills_domain())
        expense_moves = self.env['account.move'].search(self._expense_bills_domain())
        self.assertIn(move, expense_moves)
        self.assertNotIn(move, vendor_moves)

    def test_expense_bill_posting(self):
        """Standard posting still works on expense bills."""
        sheet = self.create_expense_report()
        self._post_expense_report(sheet)
        self.assertEqual(sheet.account_move_ids.state, 'posted')

    def test_expense_bill_payment_registration(self):
        """Register Payment on expense bills uses standard Odoo workflow."""
        sheet = self.create_expense_report()
        self._post_expense_report(sheet)
        move = sheet.account_move_ids
        self.assertTrue(move.is_expense_bill)
        action_context = sheet.action_register_payment()['context']
        payment = self.env['account.payment.register'].with_context(
            action_context,
        ).create({})._create_payments()
        self.assertTrue(payment)
        move.invalidate_recordset()
        self.assertIn(move.payment_state, ('paid', 'in_payment'))

    def test_category_filter_domain(self):
        """Filtering by expense category returns the correct expense bill."""
        travel_sheet = self.create_expense_report({
            'expense_line_ids': [Command.create({
                'employee_id': self.expense_employee.id,
                'product_id': self.product_a.id,
                'total_amount_currency': 50.0,
                'payment_mode': 'own_account',
                'company_id': self.company_data['company'].id,
                'date': self.frozen_today,
            })],
        })
        food_sheet = self.create_expense_report({
            'expense_line_ids': [Command.create({
                'employee_id': self.expense_employee.id,
                'product_id': self.product_b.id,
                'total_amount_currency': 75.0,
                'payment_mode': 'own_account',
                'company_id': self.company_data['company'].id,
                'date': self.frozen_today,
            })],
        })
        self._post_expense_report(travel_sheet)
        self._post_expense_report(food_sheet)
        travel_moves = self.env['account.move'].search([
            ('is_expense_bill', '=', True),
            ('expense_category_ids', 'in', self.product_a.id),
        ])
        self.assertIn(travel_sheet.account_move_ids, travel_moves)
        self.assertNotIn(food_sheet.account_move_ids, travel_moves)

    def test_category_grouping(self):
        """Group by expense category returns distinct category buckets."""
        travel_sheet = self.create_expense_report({
            'expense_line_ids': [Command.create({
                'employee_id': self.expense_employee.id,
                'product_id': self.product_a.id,
                'total_amount_currency': 50.0,
                'payment_mode': 'own_account',
                'company_id': self.company_data['company'].id,
                'date': self.frozen_today,
            })],
        })
        food_sheet = self.create_expense_report({
            'expense_line_ids': [Command.create({
                'employee_id': self.expense_employee.id,
                'product_id': self.product_b.id,
                'total_amount_currency': 75.0,
                'payment_mode': 'own_account',
                'company_id': self.company_data['company'].id,
                'date': self.frozen_today,
            })],
        })
        self._post_expense_report(travel_sheet)
        self._post_expense_report(food_sheet)
        groups = self.env['account.move'].read_group(
            domain=[('is_expense_bill', '=', True)],
            fields=['expense_category_ids'],
            groupby=['expense_category_ids'],
            lazy=False,
        )
        grouped_category_ids = {
            group['expense_category_ids'][0]
            for group in groups
            if group.get('expense_category_ids')
        }
        self.assertIn(self.product_a.id, grouped_category_ids)
        self.assertIn(self.product_b.id, grouped_category_ids)

    def test_multiple_categories_on_single_bill(self):
        """One expense report with multiple lines stores all categories on the bill."""
        sheet = self.create_expense_report({
            'expense_line_ids': [
                Command.create({
                    'employee_id': self.expense_employee.id,
                    'product_id': self.product_a.id,
                    'total_amount_currency': 100.0,
                    'payment_mode': 'own_account',
                    'company_id': self.company_data['company'].id,
                    'date': self.frozen_today,
                }),
                Command.create({
                    'employee_id': self.expense_employee.id,
                    'product_id': self.product_b.id,
                    'total_amount_currency': 200.0,
                    'payment_mode': 'own_account',
                    'company_id': self.company_data['company'].id,
                    'date': self.frozen_today,
                }),
                Command.create({
                    'employee_id': self.expense_employee.id,
                    'product_id': self.product_c.id,
                    'total_amount_currency': 50.0,
                    'payment_mode': 'own_account',
                    'company_id': self.company_data['company'].id,
                    'date': self.frozen_today,
                }),
            ],
        })
        self._post_expense_report(sheet)
        move = sheet.account_move_ids
        self.assertEqual(len(move.expense_category_ids), 3)

    def test_multi_company_isolation(self):
        """Expense bills respect company boundaries."""
        company2 = self.company_data_2['company']
        employee2 = self.env['hr.employee'].create({
            'name': 'employee company 2',
            'company_id': company2.id,
        })
        sheet = self.env['hr.expense.sheet'].create({
            'name': 'Company 2 report',
            'employee_id': employee2.id,
            'company_id': company2.id,
            'expense_line_ids': [Command.create({
                'employee_id': employee2.id,
                'product_id': self.product_c.id,
                'total_amount_currency': 80.0,
                'payment_mode': 'own_account',
                'company_id': company2.id,
                'date': self.frozen_today,
            })],
        })
        sheet._do_submit()
        sheet._do_approve()
        with self.with_company(company2):
            sheet.action_sheet_move_post()
        move = sheet.account_move_ids
        self.assertTrue(move.is_expense_bill)
        moves_c1 = self.env['account.move'].with_company(self.env.company).search([
            ('is_expense_bill', '=', True),
            ('company_id', '=', self.env.company.id),
        ])
        self.assertNotIn(move, moves_c1)
