import pandas as pd
import numpy as np
import decimal
from decimal import *
from transforms import utils
from sources.partners import string_constants
from transforms.utils import _generate_template
from transforms.partners.common import common_final_processing
import sources.partners.famulus.constants as famulus_constants
import sources.partners.waltz.constants as waltz_constants
import sources.partners.caprx.constants as caprx_constants
import sources.partners.rxpartner.constants as rxpartner_constants
import sources.partners.rxinform.constants as rxinform_constants
import sources.partners.rcopia.constants as rcopia_constants

from sources.partners.string_constants import get_partner_group

from hippo import logger

log = logger.getLogger('other_partners.py')

def _transform_rest_partners_per_chain(per_claim_fills_df, period, current_report_date, dimensions_list: [], partner=''):
    if partner == 'famulus': # for some partner we need to calculate unqie parameters/columns
        constants_module = famulus_constants # add non_otc_count column because we don't pay for otc fills
        new_columns = constants_module.UNIQUE_PARTNER_COLUMNS
    elif partner == 'waltz':
        constants_module = waltz_constants # add waltz_groupid_is_wpr column because we need to apply different partner margin depending on group id value
        new_columns = constants_module.UNIQUE_PARTNER_COLUMNS
    elif partner == 'caprx':
        constants_module = caprx_constants # add compensable_claims_count column because we need to pay partner margin only for the claims with positive admin fee
        new_columns = constants_module.UNIQUE_PARTNER_COLUMNS
    elif partner == 'rxpartner':
        constants_module = rxpartner_constants # add penny_fills and partner_penny_fills_margin columns to apply different partner margin depending on whether is a penny fill or not
        new_columns = constants_module.UNIQUE_PARTNER_COLUMNS
    else:
        new_columns = {}
    list_group_by_reversals = [f'reversal_{period}'] + dimensions_list
    list_group_by_fills = [f'fill_{period}'] + dimensions_list

    aggregate_fills_df = per_claim_fills_df.copy()
    aggregate_fills_df['penny_fill_flag'] = (
            ~aggregate_fills_df['basis_of_reimbursement_determination_resp'].eq('04') &
            (aggregate_fills_df['unc'] - aggregate_fills_df['net_revenue'] <= Decimal(0.01)) # it can be lower in case of extra sales tax
    )
    aggregate_fills_df['penny_fill_margin'] = np.where(aggregate_fills_df['penny_fill_flag']==True, aggregate_fills_df['margin'], None)
    if aggregate_fills_df.empty:
        aggregate_reversals_df = aggregate_fills_df.copy()
        aggregate_reversals_df['fill_reversal_flag'] = 'reversals'
    else:
        aggregate_fills_df['is_in_network'] = aggregate_fills_df['is_in_network'].fillna(False)
        aggregate_reversals_df = aggregate_fills_df[aggregate_fills_df[f'reversal_{period}']== f'{current_report_date}']
        aggregate_fills_df = aggregate_fills_df[aggregate_fills_df[f'fill_{period}'] == f'{current_report_date}']

        aggregate_fills_df['fill_reversal_flag'] = 'fills'
        aggregate_reversals_df['fill_reversal_flag'] = 'reversals'

        if aggregate_fills_df.empty:
            aggregate_reversals_df = utils.group_and_aggregate(aggregate_reversals_df, 'reversals', list_group_by_reversals, agg_dict_upd=new_columns,current_report_date=current_report_date, partner=partner)
            aggregate_reversals_df[period] = current_report_date

            return aggregate_fills_df, aggregate_reversals_df
        
        if aggregate_reversals_df.empty==False:
            aggregate_reversals_df = utils.group_and_aggregate(aggregate_reversals_df, 'reversals', list_group_by_reversals, agg_dict_upd=new_columns, current_report_date=current_report_date, partner=partner)
            aggregate_reversals_df[period] = current_report_date
        
        aggregate_fills_df = utils.group_and_aggregate(aggregate_fills_df, 'fills', list_group_by_fills, agg_dict_upd=new_columns, current_report_date=current_report_date, partner=partner)
        aggregate_fills_df[period] = current_report_date

    return aggregate_fills_df, aggregate_reversals_df


def _process_final_per_chain(aggregate_fills_df, aggregate_reversals_df, period, current_report_date, dimensions_list = [], partner = ''):
    ## Values
    partner_group = string_constants.get_partner_group(partner)
    LIST_OUTPUT_COLUMNS = ['partner', 'partner_group', 'fills','net_fills','new_user_fills','refills','returning_user_fills','reversals','net_revenue',
        'net_drug_costs','transaction_costs','erx_execution_costs','change_margin','hippo_margin','partner_margin','net_margin','margin_per_fill','hippo_margin_per_fill', 'ingredient_cost_upside_usd', 'dispensing_fee_upside_usd', 'margin_upside_usd', 'net_reversals', 'within_reversals'] + dimensions_list
    
    ## Conditions

    fill_column = f'fill_{period}'
    reversal_column = f'reversal_{period}'

    if aggregate_fills_df.empty and aggregate_reversals_df.empty:
    # in case both aggregate fills and reversals dataframes are empty - set final_df as empty dataframe
        final_df = _generate_template(aggregate_fills_df, partner)
        list_columns = ['partner','partner_group','fills','net_fills','new_user_fills','refills','returning_user_fills','reversals','net_revenue','net_drug_costs','transaction_costs','erx_execution_costs','change_margin','hippo_margin','partner_margin','net_margin','margin_per_fill','hippo_margin_per_fill','ingredient_cost_upside_usd','dispensing_fee_upside_usd','margin_upside_usd','net_reversals','within_reversals','chain_name','brand_generic_flag','fill_reversal_flag','new_returning_flag']
        final_df = pd.DataFrame(columns=list_columns)
        final_df = final_df.fillna(Decimal(0))
        return final_df
    elif aggregate_fills_df.empty and aggregate_reversals_df.empty==False:
    # in case only agregate reversals dataframe is not empty - set aggregate fills values to zero
        aggregate_fills_df = aggregate_reversals_df.rename(columns={f'reversal_{period}':f'fill_{period}','reversals':'fills'}).copy()
        aggregate_fills_df['fill_reversal_flag'] = 'fills'
        aggregate_fills_df[['fills','new_user_fills','returning_user_fills','hippo_net_revenue','net_drug_costs','execution_costs','margin_a','change_margin_a','processor_fee','non_otc_count','waltz_groupid_is_wpr','ingredient_cost_upside_usd','dispensing_fee_upside_usd', 'margin_upside_usd', 'net_reversals', 'within_reversals']] = Decimal(0)
        final_df = _generate_template(aggregate_fills_df, partner)
        final_df = final_df.merge(aggregate_fills_df, how='left', left_on= dimensions_list, right_on=dimensions_list, suffixes=('', '_y')).drop(columns = ['partner_y']).sort_values(f'fill_{period}')
        final_df = final_df.merge(aggregate_reversals_df, how='left', left_on= dimensions_list, right_on=dimensions_list, suffixes=('', '_y')).sort_values(f'fill_{period}')
        
        mask = (final_df.columns != fill_column) & (final_df.columns != reversal_column)

        final_df.loc[:, mask] = final_df.loc[:, mask].fillna(Decimal(0))
    elif aggregate_fills_df.empty==False and aggregate_reversals_df.empty==False:
    # merge fills and reversals only in case both dataframes are not empty
        template_final_fills_df = _generate_template(aggregate_fills_df, partner)
        template_final_reversals_df = _generate_template(aggregate_reversals_df, partner)
        final_df = pd.concat([template_final_fills_df, template_final_reversals_df]).drop_duplicates().reset_index(drop=True)
        
        final_df = final_df.merge(aggregate_fills_df, how='left', left_on= dimensions_list, right_on=dimensions_list, suffixes=('', '_y')).drop(columns = ['partner_y']).sort_values(f'fill_{period}')
        final_df = final_df.merge(aggregate_reversals_df, how='left', left_on= dimensions_list, right_on=dimensions_list, suffixes=('', '_y')).sort_values(f'fill_{period}')
        final_df = final_df[(final_df['fills'] > 0) | (final_df['reversals'] > 0)]
        
        mask = (final_df.columns != fill_column) & (final_df.columns != reversal_column)
        final_df.loc[:, mask] = final_df.loc[:, mask].fillna(Decimal(0))
    else:
    # in case only agregate reversals dataframe is empty - set reversals values to zero
        final_df = _generate_template(aggregate_fills_df, partner)
        final_df = final_df.merge(aggregate_fills_df, how='left', left_on= dimensions_list, right_on=dimensions_list, suffixes=('', '_y')).sort_values(f'fill_{period}')

        final_df[['reversals','hippo_net_revenue_y','net_drug_costs_y','margin_a_y','execution_costs_y','processor_fee_y','change_margin_a_y','non_otc_count_y','waltz_groupid_is_wpr_y','compensable_claims_count_y','new_user_reversals','returning_user_reversals','dr_first_reversal_margin', 'ingredient_cost_upside_usd_y', 'dispensing_fee_upside_usd_y', 'margin_upside_usd_y', 'net_reversals', 'within_reversals']] = Decimal(0)
        
    for col in final_df.columns:        
        if col not in [f'fill_{period}', 'contract_name', 'program_name', 'sub_program_name', 'reconciliation_program', 'reconciliation_program_annotation', 'chain_name', 'partner', 'partner_group', f'reversal_{period}', 'chain_name_y', 'partner_x', 'partner_y','margin_type', 'brand_generic_flag', 'fill_reversal_flag', 'new_returning_flag']:
            final_df[col] = final_df[col].apply(lambda x: _try_convert_to_decimal(x))
            
    final_df = common_final_processing(current_report_date, final_df=final_df, partner_group=partner_group, period=period)
    final_df = final_df[LIST_OUTPUT_COLUMNS].drop_duplicates().reset_index(drop = True)
    
    return final_df

def process_rest_partners_claims_per_chain(partner_df, period, current_report_date, dimensions_list = [], partner = ''):
    rest_partners_aggregate_fills, rest_partner_aggregate_reversals = _transform_rest_partners_per_chain(partner_df, period, current_report_date, dimensions_list, partner)
    rest_partners_aggregated_df = _process_final_per_chain(rest_partners_aggregate_fills, rest_partner_aggregate_reversals, period, current_report_date, dimensions_list, partner)

    return rest_partners_aggregated_df

# FIXME: localhost testing convert to Decimal beginning
def _try_convert_to_decimal(x):
    try:
        return Decimal(x)
    except (ValueError, InvalidOperation):
        return Decimal(0)
# FIXME: localhost testing convert to Decimal ending
