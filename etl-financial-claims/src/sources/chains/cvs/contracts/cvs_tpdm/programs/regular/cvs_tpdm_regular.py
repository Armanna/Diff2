import numpy as np

def brand_generic_indicator_cvs_tpdm_regular_vectorized(df):
    condition = (df['multi_source_code'] == 'Y') | (df['name_type_code'] == 'G') | (df['dispense_as_written'] == 'SUBSTITUTION ALLOWED BRAND DRUG DISPENSED AS A GENERIC')

    return np.where(condition, 'generic', 'brand')
