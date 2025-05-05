from decimal import *

PARTNER_MARGIN_PER_CLAIM_USD = Decimal("1.00")

UNIQUE_PARTNER_COLUMNS = {'compensable_claims_count': ('total_paid_response', lambda x: (x < 0).sum())}
