import numpy as np
import pandas as pd
from datetime import datetime
from decimal import *
from transforms import utils, pandas_helper
from transforms.utils import _generate_template
from transforms.partners.common import common_final_processing
from sources.partners import string_constants

from hippo import logger

log = logger.getLogger('good_rx.py')

def _goodrx_fill_processing_total(cpf_df, claims_df, **kwargs):

    ## Conditions
    IS_PARTNER_GOODRX_STR = "(processing_claims_and_cpf.partner == 'GoodRx')"
    IS_CPF_DIFF_ZERO_STR = "(processing_claims_and_cpf.processor_fee!=0)" 
    IS_REVERSAL_ONE_MONTH_IN_FUTURE_CFP_STR = "(processing_claims_and_cpf.valid_to > (processing_claims_and_cpf['fill_month'] + pd.DateOffset(months=+1)))"
    IS_PRICE_DIFF_U_C_STR = "(processing_claims_and_cpf.basis_of_reimbursement_determination_resp != '04')"
    IS_CPF_DIFF_ZERO = "(~processing_claims_and_cpf.processor_fee.isna())"

    ## Lists
    LIST_OUTPUT_COLUMNS = ['fill_month','total_net_fills','net_processing_fee','actual_fee_per_fill','synthetic_fee_per_fill','fee_per_fill']

    claims_df[f'fill_month'] = claims_df.valid_from.dt.to_period('M').astype('datetime64[ns]')
    claims_df[f'reversal_month'] = claims_df.valid_to.dt.to_period('M').astype('datetime64[ns]')

    processing_claims_and_cpf = claims_df.merge(cpf_df,how='left', on=['rx_id','valid_from'])

    processing_sum_df = processing_claims_and_cpf[eval(IS_PARTNER_GOODRX_STR) & eval(IS_CPF_DIFF_ZERO_STR) & eval(IS_REVERSAL_ONE_MONTH_IN_FUTURE_CFP_STR) & eval(IS_PRICE_DIFF_U_C_STR) & eval(IS_CPF_DIFF_ZERO)]
    
    fill_processing_sum_df = processing_sum_df.groupby('fill_month', as_index = False) \
        .aggregate({'npi':'size','processor_fee':'sum'}) \
        .rename(columns={'npi':'net_fills','processor_fee':'total_processing_fee'})
    processor_fee_deductable_func = lambda x: (x - Decimal(kwargs['goodrx_processor_fee_deductable_cents'])).sum()
    reversal_processing_sum_df = processing_sum_df.groupby('reversal_month', as_index = False) \
        .aggregate({'npi':'size','processor_fee': processor_fee_deductable_func}) \
        .rename(columns={'npi':'net_reversals','processor_fee':'total_processing_fee'})
    fill_processing_total_df = fill_processing_sum_df.merge(reversal_processing_sum_df, left_on='fill_month', right_on='reversal_month').reset_index(drop = True)
    fill_processing_total_df['total_net_fills'] = fill_processing_total_df.net_fills - fill_processing_total_df.net_reversals.fillna(0)
    fill_processing_total_df['net_processing_fee'] = fill_processing_total_df.total_processing_fee_x - fill_processing_total_df.total_processing_fee_y.fillna(0)
    fill_processing_total_df['actual_fee_per_fill'] = (fill_processing_total_df.net_processing_fee / fill_processing_total_df.total_net_fills).apply(lambda x: x.quantize(Decimal('0.0001'))).divide(Decimal("100"))
    fill_processing_total_df['synthetic_fee_per_fill'] = fill_processing_total_df['actual_fee_per_fill'] + (Decimal(kwargs['new_change_healthcare_fee_percentage_split']) * (Decimal(kwargs['old_change_healthcare_per_claim_fee_dollars']) - fill_processing_total_df['actual_fee_per_fill']))
    fill_processing_total_df['fee_per_fill'] = np.maximum(fill_processing_total_df.actual_fee_per_fill.values, fill_processing_total_df.synthetic_fee_per_fill.values)
    fill_processing_total_df = fill_processing_total_df[LIST_OUTPUT_COLUMNS].drop_duplicates().reset_index(drop = True)
    return fill_processing_total_df

def _goodrx_margin_rule_before_september_2024(df, **kwargs):
    """
    this function apply default contract goodrx_margin formula that was active untill September 1st 2024
    """

    df['margin_minus_fee_per_fill'] = ((df.margin - df.fee_per_fill) * Decimal(kwargs['goodrx_margin_percent'])).apply(lambda x: Decimal(x))
    df['margin_minus_processor_fee'] = ((df.margin - df.processor_fee) * Decimal(kwargs['goodrx_margin_percent'])).apply(lambda x: Decimal(x))

    # Set the flag for exclusions from the default formula
    df['good_margin_flag'] = np.where(
        ((df.unc - df.ig).apply(lambda x: x.quantize(Decimal('0.01'))) == Decimal('0.01')) |
        df.feed_ndc.isnull() |
        df.feed_npi.isnull() |
        (df.chain_name == 'costco'), True, False)

    df['good_margin'] = np.where(
        ((df.synthetic_fee_per_fill > df.actual_fee_per_fill) & (df.processor_fee != 0)),
        np.where(df.good_margin_flag, df.margin_minus_fee_per_fill.apply(lambda x: x.max(Decimal(0))),
                 np.where(df.processor_fee.isna(), Decimal(kwargs['goodrx_absolute_min_margin_dollars']),
                          df.margin_minus_fee_per_fill.apply(lambda x: x.max(Decimal(kwargs['goodrx_absolute_min_margin_dollars']))))),
        np.where(df.good_margin_flag, df.margin_minus_processor_fee.apply(lambda x: x.max(Decimal(0))),
                 np.where(df.processor_fee.isna(), Decimal(kwargs['goodrx_absolute_min_margin_dollars']),
                          df.margin_minus_processor_fee.apply(lambda x: x.max(Decimal(kwargs['goodrx_absolute_min_margin_dollars'])))))
    )
    return df

def _good_margin_rule_after_september_2024(df, **kwargs):
    """
    according to the "First Amendment" with GoodRx effective September 1, 2024 margin split for Walmart fills changed
    this function apply updated formula to calculate goodrx_margin
    """
    is_feed_ndc_null = df['feed_ndc'].isna()
    is_feed_npi_null = df['feed_npi'].isna()

    # Use quantize for precise rounding
    is_unc_ig_margin = (df['unc'] - df['ig']).apply(lambda x: x.quantize(Decimal('0.01'))) == Decimal('0.01')

    # precompute margin-minus-fee columns
    margin_minus_fee_per_fill = ((df['margin'] - df['processor_fee']) * Decimal(kwargs['goodrx_margin_percent'])).apply(lambda x: Decimal(x))
    margin_minus_processor_fee = ((df['margin'] - df['processor_fee']) * Decimal(kwargs['goodrx_margin_percent'])).apply(lambda x: Decimal(x))

    # walmart logic
    df['good_margin_walmart'] = np.where(
        is_feed_ndc_null,
        np.maximum(Decimal('0'), margin_minus_processor_fee),
        np.where(is_feed_npi_null,
                 np.maximum(Decimal('0'), margin_minus_processor_fee),
                 (df['margin'] - df['processor_fee']) * Decimal(kwargs['goodrx_margin_for_walmart_percent']))
    )

    # non-Walmart logic
    df['good_margin_non_walmart'] = np.where(
        is_feed_ndc_null,
        np.maximum(Decimal('0'), margin_minus_processor_fee),
        np.where(is_feed_npi_null,
                 np.maximum(Decimal('0'), margin_minus_processor_fee),
                 np.where(is_unc_ig_margin,
                          np.maximum(Decimal('0'), margin_minus_fee_per_fill),
                          np.maximum(margin_minus_fee_per_fill, Decimal(kwargs['goodrx_absolute_min_margin_dollars'])))
        )
    )

    df['good_margin'] = np.where(df['chain_name'] == 'walmart', df['good_margin_walmart'], df['good_margin_non_walmart'])
    return df

def _process_goodrx_per_chain(goodrx_df, fill_processing_total_df, goodrx_feed_npi_groups_df, goodrx_feed_mac_prices_df, period,  current_report_date, dimensions_list : [], partner = '', **kwargs):

    ## Values
    FILL_LIST_COLUMNS_TO_AGG = [f'fill_{period}'] + dimensions_list
    REVERSAL_LIST_COLUMNS_TO_AGG = [f'reversal_{period}'] + dimensions_list
    DICT_TO_AGG = {'good_margin': ('good_margin','sum')}
    PARTNER = partner

    # before aggregate we need to add historical_data.goodrx_feed_mac_prices_history and historical_data.goodrx_feed_npi_groups_history dataframes 
    goodrx_feed_mac_prices_df.drop_duplicates(inplace = True)

    # before aggregate we need to add historical_data.goodrx_feed_mac_prices_history and historical_data.goodrx_feed_npi_groups_history dataframes 
    goodrx_feed_mac_prices_df.drop_duplicates(inplace = True)
    goodrx_df = pandas_helper.left_join_with_condition(goodrx_df, goodrx_feed_npi_groups_df, left_on='npi', right_on='npi', filter_by = 'valid_from_x').rename(columns={'npi':'feed_npi'})
    goodrx_df = goodrx_df.drop_duplicates().reset_index(drop = True)
    goodrx_df = pandas_helper.left_join_with_condition(goodrx_df, goodrx_feed_mac_prices_df, left_on=['product_id','price_group'], right_on=['ndc11','price_group'], filter_by = 'valid_from_x').rename(columns={'ndc11':'feed_ndc'})
    goodrx_df = goodrx_df.drop_duplicates().reset_index(drop = True)

    log.info("current report date: %s", current_report_date)
    log.info("current report period: %s", period)
    fill_processing_total_df['net_processing_fee'] = fill_processing_total_df['net_processing_fee'].astype('int')

    # define the reversals GoodRx dataframe
    goodrx_reversals_df = goodrx_df[goodrx_df[f'reversal_{period}'] == f'{current_report_date}']
    goodrx_fills_df = goodrx_df[goodrx_df[f'fill_{period}'] == f'{current_report_date}']

    goodrx_fills_df['fill_reversal_flag'] = 'fills'
    goodrx_reversals_df['fill_reversal_flag'] = 'reversals'

    # merge goodrx fills and reversals with fill_processing_total_df dataframe
    goodrx_fills_df = goodrx_fills_df.merge(fill_processing_total_df, on=['fill_month'], how='left')
    goodrx_reversals_df = goodrx_reversals_df.merge(fill_processing_total_df, left_on=['reversal_month'], right_on=['fill_month'], how='left')

    # margin share for Walmart transactions changed with new GoodRx amendment effective date September, 1st 2024
    comparison_date = datetime.strptime('2024-09-01', '%Y-%m-%d').date()
    comparison_date = pd.to_datetime(comparison_date)
    # apply the margin rule before or after September 2024 based on the claim_date_of_service
    goodrx_fills_df['is_before_september_2024'] = goodrx_fills_df['claim_date_of_service'] < comparison_date
    goodrx_reversals_df['is_before_september_2024'] = goodrx_reversals_df['claim_date_of_service'] < comparison_date

    goodrx_fills_before_september_2024 = goodrx_fills_df[goodrx_fills_df['is_before_september_2024']]
    goodrx_fills_after_september_2024 = goodrx_fills_df[~goodrx_fills_df['is_before_september_2024']]
    goodrx_fills_before_september_2024 = _goodrx_margin_rule_before_september_2024(goodrx_fills_before_september_2024, **kwargs)
    goodrx_fills_after_september_2024 = _good_margin_rule_after_september_2024(goodrx_fills_after_september_2024, **kwargs)
    goodrx_fills_df = pd.concat([goodrx_fills_before_september_2024, goodrx_fills_after_september_2024])
    goodrx_reversals_before_september_2024 = goodrx_reversals_df[goodrx_reversals_df['is_before_september_2024']]
    goodrx_reversals_after_september_2024 = goodrx_reversals_df[~goodrx_reversals_df['is_before_september_2024']]
    goodrx_reversals_before_september_2024 = _goodrx_margin_rule_before_september_2024(goodrx_reversals_before_september_2024, **kwargs)
    goodrx_reversals_after_september_2024 = _good_margin_rule_after_september_2024(goodrx_reversals_after_september_2024, **kwargs)
    goodrx_reversals_df = pd.concat([goodrx_reversals_before_september_2024, goodrx_reversals_after_september_2024])
    
    aggregate_fills_goodrx_df = utils.group_and_aggregate(goodrx_fills_df, 'fills', FILL_LIST_COLUMNS_TO_AGG, agg_dict_upd=DICT_TO_AGG, current_report_date=current_report_date, partner=PARTNER)
    aggregate_reversals_goodrx_df = utils.group_and_aggregate(goodrx_reversals_df, 'reversals', REVERSAL_LIST_COLUMNS_TO_AGG, agg_dict_upd=DICT_TO_AGG, current_report_date=current_report_date, partner=PARTNER)

    return aggregate_fills_goodrx_df, aggregate_reversals_goodrx_df

def _process_final_goodrx_per_chain(aggregate_fills_df, aggregate_reversals_df, period, current_report_date, dimensions_list = []):

    ## Values
    PARTNER_STR = 'GoodRx'
    partner_group = string_constants.get_partner_group(PARTNER_STR)
    LIST_OUTPUT_COLUMNS = ['partner', 'partner_group', period, 'fills','net_fills','new_user_fills','refills',
                           'returning_user_fills','reversals','net_revenue','net_drug_costs',
                           'transaction_costs','erx_execution_costs','change_margin','partner_margin','hippo_margin','net_margin','margin_per_fill','hippo_margin_per_fill', 'ingredient_cost_upside_usd', 'dispensing_fee_upside_usd', 'margin_upside_usd', 'net_reversals', 'within_reversals'] + dimensions_list
    
    
    template_final_fills_df = _generate_template(aggregate_fills_df, PARTNER_STR)
    template_final_reversals_df = _generate_template(aggregate_reversals_df, PARTNER_STR)
    final_df = pd.concat([template_final_fills_df, template_final_reversals_df]).drop_duplicates().reset_index(drop=True)

    final_df = final_df.merge(aggregate_fills_df, how='left', left_on= dimensions_list, right_on=dimensions_list, suffixes=('', '_y')).sort_values(f'fill_{period}')
    final_df = final_df.merge(aggregate_reversals_df, how='left', left_on= dimensions_list, right_on=dimensions_list, suffixes=('', '_y')).sort_values(f'fill_{period}')
    final_df = final_df[(final_df['fills'] > 0) | (final_df['reversals'] > 0)]

    final_df[['fills','reversals','hippo_net_revenue_y','net_drug_costs_y','margin_a_y','execution_costs_y','processor_fee_y','change_margin_a_y','good_margin_y', 'ingredient_cost_upside_usd', 'ingredient_cost_upside_usd_y', 'dispensing_fee_upside_usd', 'dispensing_fee_upside_usd_y', 'margin_upside_usd', 'margin_upside_usd_y']] = \
        final_df[['fills','reversals','hippo_net_revenue_y','net_drug_costs_y','margin_a_y','execution_costs_y','processor_fee_y','change_margin_a_y','good_margin_y', 'ingredient_cost_upside_usd', 'ingredient_cost_upside_usd_y', 'dispensing_fee_upside_usd', 'dispensing_fee_upside_usd_y', 'margin_upside_usd', 'margin_upside_usd_y']].fillna(Decimal(0))

    for col in final_df.columns:
        if col not in [f'fill_{period}', 'chain_name', 'contract_name', 'program_name', 'sub_program_name', 'reconciliation_program', 'reconciliation_program_annotation', 'partner_x', f'reversal_{period}', 'chain_name_y', 'partner_y','margin_type', 'brand_generic_flag', 'fill_reversal_flag', 'new_returning_flag', 'partner', 'partner_group', 'partner_group_x', 'partner_group_y', 'non_otc_count', 'non_otc_count_y']:
            final_df[col] = final_df[col].fillna(Decimal(0))
            final_df[col] = final_df[col].apply(lambda x: _try_convert_to_decimal(x))

    final_df = common_final_processing(current_report_date, final_df=final_df, partner_group=partner_group, period = period)
    final_df = final_df[LIST_OUTPUT_COLUMNS].drop_duplicates().reset_index(drop = True)
    return final_df

def process_goodrx_claims_per_chain( claim_processing_fees_df, claims_df, goodrx_df, goodrx_feed_npi_groups_df, goodrx_feed_mac_prices_df, period, current_report_date, dimensions_list = [], partner = '', **kwargs):
    fill_processing_total_df = _goodrx_fill_processing_total(claim_processing_fees_df, claims_df, **kwargs)
    aggregate_fills_goodrx_df, aggregate_reversals_goodrx_df = _process_goodrx_per_chain(goodrx_df, fill_processing_total_df, goodrx_feed_npi_groups_df, goodrx_feed_mac_prices_df, period, current_report_date, dimensions_list, partner=partner,**kwargs)
    aggregated_goodrx_df = _process_final_goodrx_per_chain(aggregate_fills_goodrx_df, aggregate_reversals_goodrx_df, period, current_report_date, dimensions_list)
    return aggregated_goodrx_df

# FIXME: localhost testing convert to Decimal beginning
def _try_convert_to_decimal(x):
    try:
        return Decimal(x)
    except (ValueError, InvalidOperation):
        return Decimal(0)
# FIXME: localhost testing convert to Decimal ending
