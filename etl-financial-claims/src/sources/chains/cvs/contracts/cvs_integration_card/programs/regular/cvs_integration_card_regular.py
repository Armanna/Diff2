import pandas as pd
import numpy as np

def brand_generic_indicator_cvs_integration_card_regular_vectorized(df):
    condition = (df['multi_source_code'] == 'Y') | (df['name_type_code'] == 'G') | (df['dispense_as_written'] == 'SUBSTITUTION ALLOWED BRAND DRUG DISPENSED AS A GENERIC')

    # Apply the conditions using np.where
    return np.where(
        condition,
        'generic',
        'brand'
    )
