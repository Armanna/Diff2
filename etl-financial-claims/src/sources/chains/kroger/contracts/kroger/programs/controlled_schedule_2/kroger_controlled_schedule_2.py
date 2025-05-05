import pandas as pd
import numpy as np

def brand_generic_indicator_kroger_controlled_schedule_2_vectorized(df):
    return np.where(
        (df['multi_source_code'] == 'Y'),
        'generic',
        'brand'
    )
