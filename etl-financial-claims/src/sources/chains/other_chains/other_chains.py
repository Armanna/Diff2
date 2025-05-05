import pandas as pd
import numpy as np

def brand_generic_indicator_other_chains_vectorized(df):
    return np.where(
        (df['multi_source_code'] == 'Y'),
        'generic',
        'brand'
    )
