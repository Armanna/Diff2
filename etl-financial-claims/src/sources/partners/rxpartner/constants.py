from decimal import *

PARTNER_MARGIN_PER_CLAIM_USD = Decimal("4.00")
PARTNER_PENNY_FILL_PERCENTAGE = Decimal("0.9")

UNIQUE_PARTNER_COLUMNS = {'penny_fills': ('penny_fill_flag', lambda flag: (flag == True).sum()), 'partner_penny_fills_margin': ('penny_fill_margin', lambda margin: (margin * PARTNER_PENNY_FILL_PERCENTAGE).sum())}
