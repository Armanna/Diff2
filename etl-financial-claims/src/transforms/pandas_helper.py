import pandas as pd
from datetime import datetime
import numpy as np

def left_join_with_condition(df1, df2, left_on, right_on, filter_by = 'claim_date_of_service'):
    '''
    this method helps to perform SQL-like left join with additional datetime-based conditions. 
    it's important to double check for duplicated column names since it will lead to index error during pd.concat().
    '''
    df1.reset_index(inplace=True, drop=True)
    df1['row_number'] = df1.reset_index().index

    merged_df = pd.merge(df1, df2, how = 'left', left_on = left_on, right_on = right_on)
    if filter_by == 'claim_date_of_service':
        merged_df = merged_df.loc[np.where((merged_df[filter_by].values >= merged_df.valid_from_y.values) & (merged_df[filter_by].values < merged_df.valid_to_y.values))].rename(columns={'valid_from_x':'valid_from','valid_to_x':'valid_to'}).drop(columns=['valid_from_y','valid_to_y'])
    else:
        merged_df = merged_df.loc[np.where((merged_df[filter_by].values  >= merged_df.valid_from_y.values ) & (merged_df[filter_by].values  < merged_df.valid_to_y.values ))].rename(columns={'valid_from_x':'valid_from','valid_to_x':'valid_to'}).drop(columns=['valid_from_y','valid_to_y'])
    df1 = pd.concat([merged_df,df1[~df1['row_number'].isin(merged_df.row_number)]])

    return df1.drop(columns=['row_number'])

def left_join_with_condition_preserve_index(df1, df2, left_on, right_on, filter_by='claim_date_of_service'):
    '''
    The difference between this method and above is that
    this method preserves index instead of mutating it. It's required for future vectorized filtering (masking) operations
    '''
    original_index = df1.index
    df1 = df1.reset_index(drop=True)
    df1['row_number'] = df1.index

    merged_df = pd.merge(df1, df2, how='left', left_on=left_on, right_on=right_on)
    
    if filter_by == 'claim_date_of_service':
        condition = (merged_df[filter_by] >= merged_df['valid_from_y']) & (merged_df[filter_by] < merged_df['valid_to_y'])
        merged_df = merged_df.loc[condition].drop(columns=['valid_from_y', 'valid_to_y'])
    else:
        condition = (merged_df[filter_by] >= merged_df['valid_from_y']) & (merged_df[filter_by] < merged_df['valid_to_y'])
        merged_df = merged_df.loc[condition].drop(columns=['valid_from_y', 'valid_to_y'])

    # Correct the column renaming after filtering
    merged_df = merged_df.rename(columns={'valid_from_x': 'valid_from', 'valid_to_x': 'valid_to'})

    # Ensure the original order is preserved by reindexing merged_df
    merged_df = merged_df.sort_values(by='row_number')
    
    # Add back the rows that were not matched
    unmatched_rows = df1[~df1['row_number'].isin(merged_df['row_number'])]
    df1 = pd.concat([merged_df, unmatched_rows], ignore_index=True).sort_values(by='row_number')
    
    df1 = df1.drop(columns=['row_number']).set_index(original_index)

    return df1
