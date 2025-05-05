import pandas as pd
import numpy as np

def brand_generic_indicator_cvs_regular_vectorized(df):
    condition_1 = (df['claim_date_of_service'] < pd.to_datetime('2024-07-01 00:00:00')) | (df['valid_from'] < pd.to_datetime('2024-07-01 10:30:00'))
    condition_2a = (df['multi_source_code'] == 'Y') | (df['dispense_as_written'] == 'SUBSTITUTION ALLOWED BRAND DRUG DISPENSED AS A GENERIC')
    condition_2b = (df['multi_source_code'] == 'Y') | (df['name_type_code'] == 'G') | (df['dispense_as_written'] == 'SUBSTITUTION ALLOWED BRAND DRUG DISPENSED AS A GENERIC')

    # Apply the conditions using np.where
    return np.where(
        condition_1,
        np.where(condition_2a, 'generic', 'brand'),
        np.where(condition_2b, 'generic', 'brand')
    )
