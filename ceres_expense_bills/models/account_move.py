# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_expense_bill = fields.Boolean(
        string='Expense Bill',
        compute='_compute_is_expense_bill',
        store=True,
        index=True,
        help=(
            'True when this accounting record is linked to an expense report '
            '(hr.expense.sheet) through account.move.expense_sheet_id.'
        ),
    )
    expense_category_ids = fields.Many2many(
        comodel_name='product.product',
        relation='account_move_expense_category_rel',
        column1='move_id',
        column2='product_id',
        string='Expense Categories',
        compute='_compute_expense_category_ids',
        store=True,
        readonly=True,
        help=(
            'Expense categories from all lines on the linked expense report. '
            'A single bill may include multiple categories.'
        ),
    )
    expense_employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        relation='account_move_expense_employee_rel',
        column1='move_id',
        column2='employee_id',
        string='Expense Employees',
        compute='_compute_expense_employee_ids',
        store=True,
        readonly=True,
        help='Employees from expense lines on the linked expense report.',
    )

    @api.depends('expense_sheet_id')
    def _compute_is_expense_bill(self):
        """Flag moves created by hr_expense via expense_sheet_id (Odoo 18)."""
        for move in self:
            move.is_expense_bill = bool(move.expense_sheet_id)

    @api.depends('expense_sheet_id.expense_line_ids.product_id')
    def _compute_expense_category_ids(self):
        """Aggregate categories from expense report lines (multi-category safe)."""
        for move in self:
            if move.expense_sheet_id:
                move.expense_category_ids = move.expense_sheet_id.expense_line_ids.product_id
            else:
                move.expense_category_ids = False

    @api.depends('expense_sheet_id.expense_line_ids.employee_id')
    def _compute_expense_employee_ids(self):
        """Aggregate employees from expense report lines for search/group-by."""
        for move in self:
            if move.expense_sheet_id:
                move.expense_employee_ids = move.expense_sheet_id.expense_line_ids.employee_id
            else:
                move.expense_employee_ids = False

    @api.constrains('expense_sheet_id', 'expense_category_ids')
    def _check_expense_bill_categories(self):
        """Stored categories must match linked expense report lines."""
        for move in self.filtered('is_expense_bill'):
            sheet_products = move.expense_sheet_id.expense_line_ids.product_id
            if move.expense_category_ids - sheet_products:
                raise ValidationError(_(
                    "Expense categories on %(bill)s do not match the linked expense report.",
                    bill=move.display_name,
                ))
            invalid_products = sheet_products.filtered(lambda product: not product.can_be_expensed)
            if invalid_products:
                raise ValidationError(_(
                    "Expense bill %(bill)s references products that are not expense categories: %(products)s",
                    bill=move.display_name,
                    products=', '.join(invalid_products.mapped('display_name')),
                ))

    @api.constrains('expense_sheet_id', 'move_type')
    def _check_expense_bill_move_type(self):
        """Expense reports create vendor bills or payment journal entries."""
        allowed_types = {'in_invoice', 'in_refund', 'entry'}
        for move in self.filtered('is_expense_bill'):
            if move.move_type not in allowed_types:
                raise ValidationError(_(
                    "Expense bill %(bill)s has unsupported move type %(move_type)s.",
                    bill=move.display_name,
                    move_type=move.move_type,
                ))

    @api.model
    def _get_vendor_bills_domain(self):
        """Standard Odoo 18 vendor bills domain, excluding expense bills."""
        return [
            ('move_type', 'in', ['in_invoice', 'in_refund']),
            ('is_expense_bill', '=', False),
        ]

    @api.model
    def _get_expense_bills_domain(self):
        return [('is_expense_bill', '=', True)]
