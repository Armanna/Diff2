from decimal import *

PARTNER_MARGIN_PER_CLAIM_USD = Decimal("3.00")

UNIQUE_PARTNER_COLUMNS = {'non_otc_count': ('is_otc', lambda x: (x == False).sum())}
