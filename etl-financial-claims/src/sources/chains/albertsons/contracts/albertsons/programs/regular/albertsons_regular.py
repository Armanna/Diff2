from datetime import datetime

import numpy as np

# Albertsons allows daw codes 1, 2 and 9 to be reconciled as brand
is_brand_daw = ['SUBSTITUTION NOT ALLOWED BY PRESCRIBER', 'SUBSTITUTION ALLOWED PATIENT REQUESTED PRODUCT DISPENSED',
'SUBSTITUTION ALLOWED BY PRESCRIBER BUT PLAN REQUESTS BRAND PATIENT PLAN REQUESTED BRAND PRODUCT']

def brand_generic_indicator_albertsons_regular_vectorized(df):
    mask_generic = (
            (df['nadac_is_generic'] == 'True')  |
            (df['nadac_is_generic'].isnull() & (df['multi_source_code'] == 'Y')) |
            (
                df['nadac_is_generic'].isnull()
                & (df['multi_source_code'] == 'M')
                & (df['name_type_code'] == 'G')
            ) |
            (
                    df['nadac_is_generic'].isnull()
                    & (df['multi_source_code'] == 'O')
                    & (df['name_type_code'] == 'G')
                    & (~df['dispense_as_written'].isin(is_brand_daw))
            )
    )

    return np.where(mask_generic, 'generic', 'brand')
