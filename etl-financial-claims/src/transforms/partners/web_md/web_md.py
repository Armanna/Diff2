import pandas as pd
import numpy as np
from decimal import *
from datetime import datetime
from transforms import utils
from sources.partners import string_constants
from transforms.utils import _generate_template
from transforms.partners.common import common_final_processing
from sources.partners.string_constants import get_partner_group

from hippo import logger

log = logger.getLogger('webmd.py')

def webmd_margin(row):
    if (row['net_fills'] - row['net_penny_fills']) <= 15000:    # check if the 15000 fills condition is met
        return Decimal('4.5') * (row['net_fills'] - row['net_penny_fills'])
    else:
        return Decimal('67500') + row['net_penny_fill_profit'] * Decimal('0.5') + max((row['gross_profit_from_15000_onwards'] - row['gross_profit_from_15000_onwards_r']) * Decimal('0.5'), ((row['net_fills'] - row['net_penny_fills']) - Decimal('15000')) * Decimal('3.0'))

def _transform_webmd_per_chain(per_claim_fills_df, report_date, period, dimensions_list = [], partner = ''):
    per_claim_fills_df['penny_fill_flag'] = (
        ~per_claim_fills_df['basis_of_reimbursement_determination_resp'].eq('04') &
        (per_claim_fills_df['unc'] - per_claim_fills_df['net_revenue'] <= Decimal(0.01)) # it can be lower in case of extra sales tax
    )
    if per_claim_fills_df.empty:
        aggregate_reversals_df = per_claim_fills_df.copy()
        aggregated_webmd_dict = {'webmd_fill': per_claim_fills_df, 'webmd_reversal': aggregate_reversals_df}
        return aggregated_webmd_dict
    else:
        aggregate_reversals_df = per_claim_fills_df[per_claim_fills_df[f'reversal_{period}'] == f'{report_date}']
        aggregate_fills_df = per_claim_fills_df[per_claim_fills_df[f'fill_{period}'] == f'{report_date}']
        aggregated_webmd_dict = {}
        fills_reversals_df_dict = {'fills': aggregate_fills_df, 'reversals': aggregate_reversals_df} if aggregate_reversals_df.empty==False else {'fills': aggregate_fills_df}

        for key, df in fills_reversals_df_dict.items():
            df['gross_profit'] = df.margin - df.processor_fee
            df['fill_reversal_flag'] = key

            non_penny_df = df[df['penny_fill_flag'] == False].copy()
            penny_df = df[df['penny_fill_flag'] == True].copy()

            non_penny_df['row_num'] = np.arange(1, len(non_penny_df) + 1)
            non_penny_df['gross_profit_from_15000_onwards'] = np.where(
                non_penny_df['row_num'] > 15000,
                non_penny_df['gross_profit'],
                Decimal(0)
            )
            penny_df['gross_profit_from_15000_onwards'] = Decimal(0)
            combined_df = pd.concat([non_penny_df.drop(columns=['row_num']), penny_df]).drop_duplicates().reset_index(drop=True)

            aggregated_df = utils.group_and_aggregate(combined_df, key, [f'{key[:-1]}_{period}'] + dimensions_list + ['penny_fill_flag', 'gross_profit_from_15000_onwards'], agg_dict_upd={'gross_profit': ('gross_profit','sum')}, current_report_date=report_date, partner = partner)
            aggregated_df[period] = report_date

            penny_true_flag = (aggregated_df['penny_fill_flag'] == True)
            
            aggregated_df['gross_penny_fill_profit'] = np.where(
                penny_true_flag,
                aggregated_df['gross_profit'],
                0
            )

            aggregated_df['penny_fills'] = np.where(
                penny_true_flag,
                aggregated_df[key],
                0
            )
            
            aggregated_webmd_dict.update({f'webmd_{key[:-1]}': aggregated_df})
        if aggregate_reversals_df.empty:
            aggregated_webmd_dict.update({f'webmd_reversal': aggregate_reversals_df})
    return aggregated_webmd_dict

def _process_final_webmd_per_chain(aggregate_fills_df, aggregate_reversals_df, period, current_report_date, dimensions_list, partner):
    ## Values
    PARTNER_STR = partner
    partner_group = string_constants.get_partner_group(partner)
    LIST_OUTPUT_COLUMNS = ['partner','partner_group',period,'fills','net_fills','new_user_fills','refills','returning_user_fills','reversals','net_revenue',
    'net_drug_costs','transaction_costs','erx_execution_costs','change_margin','hippo_margin','partner_margin','net_margin','margin_per_fill','hippo_margin_per_fill', 'ingredient_cost_upside_usd', 'dispensing_fee_upside_usd', 'margin_upside_usd', 'net_reversals', 'within_reversals'] + dimensions_list

    ## Conditions
    COLUMNS_DIFF_FILL_PERIOD_STR = "(final_df.columns != f'fill_{period}')"
    COLUMNS_DIFF_REVERSAL_PERIOD_STR = "(final_df.columns != f'reversal_{period}')"

    if aggregate_fills_df.empty and aggregate_reversals_df.empty:
    # in case both aggregate fills and reversals dataframes are empty - set final_df as empty dataframe
        final_df = _generate_template(aggregate_fills_df, PARTNER_STR)
        final_df = final_df.merge(aggregate_fills_df, how='left', left_on= dimensions_list, right_on=dimensions_list, suffixes=('', '_y')).sort_values(f'fill_{period}')
        final_df = final_df.fillna(Decimal(0))
        final_df.loc[:, eval(COLUMNS_DIFF_FILL_PERIOD_STR) & eval(COLUMNS_DIFF_REVERSAL_PERIOD_STR)] = final_df.loc[:, eval(COLUMNS_DIFF_FILL_PERIOD_STR) & eval(COLUMNS_DIFF_REVERSAL_PERIOD_STR)].fillna(Decimal(0))

        return final_df
    elif aggregate_fills_df.empty and aggregate_reversals_df.empty==False:
    # in case only agregate reversals dataframe is not empty - set aggregate fills values to zero
        final_df = _generate_template(aggregate_reversals_df, PARTNER_STR)
        final_df = final_df.merge(aggregate_reversals_df, how='left', left_on= dimensions_list, right_on=dimensions_list, suffixes=('', '_y')).sort_values(f'fill_{period}')
        final_df.loc[:, eval(COLUMNS_DIFF_FILL_PERIOD_STR) & eval(COLUMNS_DIFF_REVERSAL_PERIOD_STR)] = final_df.loc[:, eval(COLUMNS_DIFF_FILL_PERIOD_STR) & eval(COLUMNS_DIFF_REVERSAL_PERIOD_STR)].fillna(Decimal(0))

    elif aggregate_fills_df.empty==False and aggregate_reversals_df.empty==False:
    # merge fills and reversals only in case both dataframes are not empty
        template_final_fills_df = _generate_template(aggregate_fills_df, PARTNER_STR)
        template_final_reversals_df = _generate_template(aggregate_reversals_df, PARTNER_STR)
        final_df = pd.concat([template_final_fills_df, template_final_reversals_df]).drop_duplicates().reset_index(drop=True)

        final_df = final_df.merge(aggregate_fills_df, how='left', left_on= dimensions_list, right_on=dimensions_list, suffixes=('', '_y')).drop(columns = ['partner_y']).sort_values(f'fill_{period}')
        final_df = final_df.merge(aggregate_reversals_df, how='left', left_on= dimensions_list, right_on=dimensions_list, suffixes=('', '_y')).sort_values(f'fill_{period}')
        final_df = final_df[(final_df['fills'] > 0) | (final_df['reversals'] > 0)]

        final_df[['reversals','hippo_net_revenue_y','net_drug_costs_y','margin_a_y','execution_costs_y','processor_fee_y','change_margin_a_y','penny_fills_y','gross_profit_y','gross_penny_fill_profit_y', 'new_user_fills', 'returning_user_fills', 'fills']] = \
        final_df[['reversals','hippo_net_revenue_y','net_drug_costs_y','margin_a_y','execution_costs_y','processor_fee_y','change_margin_a_y','penny_fills_y','gross_profit_y','gross_penny_fill_profit_y', 'new_user_fills', 'returning_user_fills', 'fills']].fillna(Decimal(0))

        for col in final_df.columns:
            if col not in [f'fill_{period}', 'chain_name', 'partner', 'partner_group', 'contract_name', 'program_name', 'sub_program_name', 'reconciliation_program', 'reconciliation_program_annotation', f'reversal_{period}', 'chain_name_y', 'partner_x', 'partner_y', 'partner_group_x', 'partner_group_y', 'margin_type', 'brand_generic_flag', 'fill_reversal_flag', 'new_returning_flag']:
                final_df[col] = final_df[col].fillna(Decimal(0))
                final_df[col] = final_df[col].apply(lambda x: _try_convert_to_decimal(x))
    else:
    # in case only agregate reversals dataframe is empty - set reversals values to zero
        final_df = aggregate_fills_df.copy()
        final_df[['reversals','hippo_net_revenue_y','net_drug_costs_y','margin_a_y','execution_costs_y','processor_fee_y','change_margin_a_y','new_user_reversals','returning_user_reversals','dr_first_reversal_margin','penny_fills_y','gross_profit_y','gross_penny_fill_profit_y', 'gross_profit_from_15000_onwards_y', 'ingredient_cost_upside_usd_y', 'dispensing_fee_upside_usd_y', 'margin_upside_usd_y', 'net_reversals', 'within_reversals']] = Decimal(0)
        final_df['partner_group'] = partner_group

    final_df = common_final_processing(current_report_date, final_df=final_df, partner_group=partner_group, period=period)
    
    final_df = final_df[LIST_OUTPUT_COLUMNS].drop_duplicates().reset_index(drop = True)
    return final_df


def process_webmd_claims_per_chain(partner_df, report_date, period, dimensions_list = [], partner = ''):
    aggregated_webmd_dict = _transform_webmd_per_chain(partner_df, report_date, period, dimensions_list, partner)
    webmd_aggregated_df = _process_final_webmd_per_chain(aggregated_webmd_dict['webmd_fill'], aggregated_webmd_dict['webmd_reversal'], period, report_date, dimensions_list, partner)

    return webmd_aggregated_df


# FIXME: localhost testing convert to Decimal beginning
def _try_convert_to_decimal(x):
    try:
        return Decimal(x)
    except (ValueError, InvalidOperation):
        return Decimal(0)
# FIXME: localhost testing convert to Decimal ending
