import pandas as pd
import numpy as np

def brand_generic_indicator_rite_aid_irreconcilable_vectorized(df):
    return np.where(
        pd.isna(df['nadac_is_generic']) & (df['multi_source_code'] == 'Y'),
        'generic',
        np.where(
            pd.isna(df['nadac_is_generic']) & (df['multi_source_code'] == 'M') & (df['name_type_code'] == 'G'),
            'generic',
            np.where(
                df['nadac_is_generic'] == 'True',
                'generic',
                'brand'
            )
        )
    )
