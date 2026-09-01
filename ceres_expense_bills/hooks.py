# -*- coding: utf-8 -*-


def post_init_hook(env):
    """Backfill stored fields on moves already linked to expense reports."""
    moves = env['account.move'].search([('expense_sheet_id', '!=', False)])
    if moves:
        moves._compute_is_expense_bill()
        moves._compute_expense_category_ids()
        moves._compute_expense_employee_ids()
