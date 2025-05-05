import pandas as pd
import numpy as np

def brand_generic_indicator_harris_teeter_regular_vectorized(df):
    return np.where(
        (df['multi_source_code'] == 'Y'),
        'generic',
        'brand'
    )
