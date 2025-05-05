from decimal import *

CHAIN_PHARMACY_LICENSEES_MARGIN_USD = Decimal("3.00")
CUSTOMER_LICENSEES_MARGIN_USD = Decimal("4.00")

UNIQUE_PARTNER_COLUMNS = {'waltz_groupid_is_wpr': ('group_id', lambda x: (x == 'WPR').sum())}
