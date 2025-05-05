from datetime import datetime

import numpy as np

is_brand_daw = ['SUBSTITUTION NOT ALLOWED BY PRESCRIBER', 'SUBSTITUTION ALLOWED PATIENT REQUESTED PRODUCT DISPENSED',
'SUBSTITUTION NOT ALLOWED BRAND DRUG MANDATED BY LAW']

def brand_generic_indicator_health_mart_atlas_regular_vectorized(df):
    mask_generic = (
            (df['nadac_is_generic'] == 'True') |
            (df['nadac_is_generic'].isnull() & (df['multi_source_code'] == 'Y')) |
            ((df['multi_source_code'] == 'O') & (~df['dispense_as_written'].isin(is_brand_daw)))
    )

    return np.where(mask_generic, 'generic', 'brand')
