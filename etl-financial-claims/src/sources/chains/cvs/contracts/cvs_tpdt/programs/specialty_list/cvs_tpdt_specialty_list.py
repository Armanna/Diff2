import pandas as pd
import numpy as np

def brand_generic_indicator_cvs_tpdt_specialty_vectorized(df):
    return np.where(
        (df['multi_source_code'] == 'Y') | 
        (df['dispense_as_written'] == 'SUBSTITUTION ALLOWED BRAND DRUG DISPENSED AS A GENERIC'),
        'generic',
        'brand'
    )
