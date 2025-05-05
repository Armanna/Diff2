import pandas as pd
import numpy as np

is_generic_daw = [
    'SUBSTITUTION ALLOWED PHARMACIST SELECTED PRODUCT DISPENSED',
    'SUBSTITUTION ALLOWED GENERIC DRUG NOT IN STOCK',
    'SUBSTITUTION ALLOWED BRAND DRUG DISPENSED AS A GENERIC',
    'OVERRIDE'
]

def brand_generic_indicator_rite_aid_regular_vectorized(df):
    condition_1 = (df['claim_date_of_service'] < pd.to_datetime('2025-04-01 00:00:00'))
    # Condition from the original contract
    condition_2a = ((pd.isna(df['nadac_is_generic']) & (df['multi_source_code'] == 'Y')) | (pd.isna(df['nadac_is_generic']) & (df['multi_source_code'] == 'M') & (df['name_type_code'] == 'G')) | (df['nadac_is_generic'] == 'True'))
    # Condition from the first amendment
    condition_2b = (df['multi_source_code'] == 'Y') | ((df['multi_source_code'] == 'O')  & (df['dispense_as_written'].isin(is_generic_daw)))
    return np.where(
        condition_1,
        np.where(condition_2a, 'generic', 'brand'),
        np.where(condition_2b, 'generic', 'brand')
    )
