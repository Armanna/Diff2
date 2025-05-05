import pandas as pd
import numpy as np

def brand_generic_indicator_walmart_regular_vectorized(df):
    return np.where(
        df['nadac_is_generic'] == 'True',
        'generic',
        np.where(
            (df['nadac_is_generic'] == 'True') & pd.notna(df['nadac']),
            'generic',
            np.where(
                pd.isna(df['nadac_is_generic']) & pd.notna(df['gpi_nadac']),
                'generic',
                np.where(
                    pd.isna(df['nadac_is_generic']) & (df['multi_source_code'] == 'Y'),
                    'generic',
                    'brand'
                )
            )
        )
    )
