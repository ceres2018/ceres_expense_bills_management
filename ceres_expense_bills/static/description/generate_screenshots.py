#!/usr/bin/env python3
"""Generate Odoo Apps screenshots for ceres_expense_bills_management."""

from pathlib import Path

try:
    import cairosvg
except ImportError:
    raise SystemExit('pip install cairosvg')

OUT = Path(__file__).resolve().parent / 'screenshots'
ICON_OUT = Path(__file__).resolve().parent
W, H = 876, 500


def shell(title, body, breadcrumb='Expenses / Expense Bills'):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#f0f2f5"/>
  <rect width="{W}" height="48" fill="#714b67"/>
  <text x="20" y="30" fill="#fff" font-family="Arial,sans-serif" font-size="16" font-weight="700">Odoo</text>
  <text x="120" y="30" fill="#fff" font-family="Arial,sans-serif" font-size="14">{breadcrumb}</text>
  <rect x="0" y="48" width="190" height="{H - 48}" fill="#fff" stroke="#d8dadd"/>
  <text x="20" y="88" fill="#714b67" font-family="Arial,sans-serif" font-size="13" font-weight="700">Expenses</text>
  <text x="28" y="118" fill="#0f766e" font-family="Arial,sans-serif" font-size="12" font-weight="700">Expense Bills</text>
  <text x="28" y="142" fill="#666" font-family="Arial,sans-serif" font-size="12">My Expenses</text>
  <text x="28" y="164" fill="#666" font-family="Arial,sans-serif" font-size="12">Reporting</text>
  {body}
  <text x="20" y="{H - 14}" fill="#888" font-family="Arial,sans-serif" font-size="11">{title}</text>
</svg>'''


def menu_shot():
    body = '''
  <rect x="210" y="108" width="640" height="360" fill="#fff" stroke="#d8dadd"/>
  <text x="226" y="142" fill="#111" font-family="Arial,sans-serif" font-size="18" font-weight="700">Expense Bills</text>
  <text x="226" y="168" fill="#666" font-family="Arial,sans-serif" font-size="12">Open from Expenses application menu</text>'''
    return shell('Expenses menu with Expense Bills entry', body)


def list_shot():
    rows = ''
    y = 200
    for ref, partner, cats, total, status in [
        ('BILL/2025/0042', 'John Smith', 'Travel', '1,250.00', 'Posted'),
        ('BILL/2025/0041', 'Jane Doe', 'Food, Travel', '520.00', 'Paid'),
        ('BILL/2025/0038', 'Alex Lee', 'Fuel', '890.00', 'Not Paid'),
    ]:
        rows += f'''
  <rect x="210" y="{y}" width="640" height="40" fill="#fff" stroke="#e9ecef"/>
  <text x="222" y="{y + 24}" font-family="Arial,sans-serif" font-size="12" fill="#111">{ref}</text>
  <text x="340" y="{y + 24}" font-family="Arial,sans-serif" font-size="12" fill="#444">{partner}</text>
  <text x="470" y="{y + 24}" font-family="Arial,sans-serif" font-size="12" fill="#0f766e">{cats}</text>
  <text x="590" y="{y + 24}" font-family="Arial,sans-serif" font-size="12" fill="#111">{total}</text>
  <text x="700" y="{y + 24}" font-family="Arial,sans-serif" font-size="12" fill="#666">{status}</text>'''
        y += 42
    header = '''
  <rect x="210" y="108" width="640" height="56" fill="#fff" stroke="#d8dadd"/>
  <text x="226" y="142" fill="#111" font-family="Arial,sans-serif" font-size="18" font-weight="700">Expense Bills</text>
  <rect x="210" y="164" width="640" height="32" fill="#f8f9fa" stroke="#e9ecef"/>
  <text x="222" y="184" font-family="Arial,sans-serif" font-size="11" fill="#666">Bill | Partner | Categories | Total | Status</text>'''
    return shell('Expense Bills list view', header + rows)


def filter_shot():
    body = '''
  <rect x="210" y="108" width="150" height="360" fill="#fff" stroke="#d8dadd"/>
  <text x="226" y="136" fill="#111" font-family="Arial,sans-serif" font-size="13" font-weight="700">Expense Category</text>
  <text x="226" y="168" fill="#0f766e" font-family="Arial,sans-serif" font-size="12" font-weight="700">All (12)</text>
  <text x="226" y="194" fill="#444" font-family="Arial,sans-serif" font-size="12">Travel (4)</text>
  <text x="226" y="218" fill="#444" font-family="Arial,sans-serif" font-size="12">Food (3)</text>
  <text x="226" y="242" fill="#444" font-family="Arial,sans-serif" font-size="12">Fuel (2)</text>
  <rect x="380" y="108" width="470" height="360" fill="#fff" stroke="#d8dadd"/>
  <text x="396" y="142" fill="#111" font-family="Arial,sans-serif" font-size="18" font-weight="700">Filtered: Travel</text>'''
    return shell('Dynamic expense category filters', body)


def groupby_shot():
    body = '''
  <rect x="210" y="108" width="640" height="360" fill="#fff" stroke="#d8dadd"/>
  <text x="226" y="142" fill="#111" font-family="Arial,sans-serif" font-size="18" font-weight="700">Group By: Expense Category</text>
  <text x="226" y="180" fill="#0f766e" font-family="Arial,sans-serif" font-size="14" font-weight="700">Travel (4 bills)</text>
  <text x="226" y="220" fill="#0f766e" font-family="Arial,sans-serif" font-size="14" font-weight="700">Food (3 bills)</text>
  <text x="226" y="260" fill="#0f766e" font-family="Arial,sans-serif" font-size="14" font-weight="700">Fuel (2 bills)</text>'''
    return shell('Group by expense category', body)


def vendor_shot():
    body = '''
  <rect x="210" y="108" width="640" height="56" fill="#fff" stroke="#d8dadd"/>
  <text x="226" y="142" fill="#111" font-family="Arial,sans-serif" font-size="18" font-weight="700">Vendor Bills</text>
  <rect x="210" y="180" width="640" height="34" fill="#ecfdf5" stroke="#99f6e4"/>
  <text x="222" y="201" fill="#0f766e" font-family="Arial,sans-serif" font-size="12">Expense bills excluded (is_expense_bill = False)</text>
  <rect x="210" y="220" width="640" height="40" fill="#fff" stroke="#e9ecef"/>
  <text x="222" y="246" fill="#111" font-family="Arial,sans-serif" font-size="12">BILL/2025/0101 - Office Supplies Co.</text>'''
    return shell('Vendor Bills without expense bills', body, 'Accounting / Vendors / Bills')


ICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <rect width="256" height="256" rx="48" fill="#0f766e"/>
  <rect x="52" y="58" width="152" height="108" rx="12" fill="#ecfdf5" stroke="#99f6e4" stroke-width="4"/>
  <rect x="72" y="82" width="88" height="10" rx="5" fill="#14b8a6"/>
  <rect x="72" y="102" width="112" height="8" rx="4" fill="#5eead4"/>
  <circle cx="188" cy="178" r="28" fill="#fbbf24"/>
  <path d="M176 178h24M188 166v24" stroke="#78350f" stroke-width="6" stroke-linecap="round"/>
</svg>'''


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    shots = {
        'expense_bills_menu.png': menu_shot(),
        'expense_bills_list.png': list_shot(),
        'expense_bills_filters.png': filter_shot(),
        'expense_bills_groupby.png': groupby_shot(),
        'vendor_bills_separation.png': vendor_shot(),
    }
    for name, svg in shots.items():
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(OUT / name), output_width=W, output_height=H)
        print(name)
    cairosvg.svg2png(bytestring=ICON.encode(), write_to=str(ICON_OUT / 'icon.png'), output_width=256, output_height=256)
    print('icon.png')
