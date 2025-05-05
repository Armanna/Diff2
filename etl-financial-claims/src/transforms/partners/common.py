import pandas as pd
import numpy as np
from decimal import *
import sources.partners.famulus.constants as famulus_constants
import sources.partners.caprx.constants as caprx_constants
import sources.partners.rxpartner.constants as rxpartner_constants
import sources.partners.waltz.constants as waltz_constants
import sources.partners.rxlink.constants as rxlink_constants
import sources.partners.rxinform.constants as rxinform_constants
import sources.partners.rcopia.constants as rcopia_constants
import sources.chains.cvs.contracts.cvs_tpdt.programs.regular.constants as cvs_tpdt
import sources.chains.cvs.contracts.cvs_tpdm.programs.regular.constants as cvs_tpdm
from datetime import datetime
from hippo import logger

log = logger.getLogger('common.py')

## COMMON
def common_final_processing(current_report_date, final_df: pd.DataFrame, partner_group : str, **kwargs) -> pd.DataFrame:
    PERIOD_STR = kwargs['period']

    ## Conditions
    final_df['net_fills'] = final_df.fills - final_df.reversals
    final_df['net_fills'] = final_df['net_fills'].apply(lambda x: Decimal(x))
    final_df['net_revenue'] = final_df.hippo_net_revenue - final_df.hippo_net_revenue_y
    final_df['net_drug_costs'] = final_df.net_drug_costs - final_df.net_drug_costs_y
    final_df['transaction_costs'] = final_df.processor_fee - final_df.processor_fee_y
    final_df['net_margin'] = final_df.margin_a - final_df.margin_a_y
    final_df['change_margin'] = final_df.change_margin_a - final_df.change_margin_a_y
    final_df['ingredient_cost_upside_usd'] = final_df['ingredient_cost_upside_usd'] - final_df['ingredient_cost_upside_usd_y']
    final_df['dispensing_fee_upside_usd'] = final_df['dispensing_fee_upside_usd'] - final_df['dispensing_fee_upside_usd_y']
    final_df['margin_upside_usd'] = final_df['margin_upside_usd'] - final_df['margin_upside_usd_y']

    if partner_group  not in ['GoodRx', 'webmd']:                                                      ## OTHER PARTNERS AND RXINFORM AND RCOPIA
        final_df['negative_net_fills'] = -final_df['net_fills']
        final_df['erx_execution_costs'] = final_df.execution_costs - final_df.execution_costs_y
        final_df['partner_margin'] = Decimal(0)

        if partner_group in ['other']:
            final_df['hippo_margin'] = final_df.net_margin - final_df.change_margin - final_df.erx_execution_costs + final_df.negative_net_fills
        elif partner_group in ['caprx']:
            final_df['compensable_claims'] = final_df.compensable_claims_count - final_df.compensable_claims_count_y
            final_df['partner_margin'] = final_df['compensable_claims'] * caprx_constants.PARTNER_MARGIN_PER_CLAIM_USD
            final_df['hippo_margin'] = final_df.net_margin - final_df.change_margin - final_df.erx_execution_costs - final_df.partner_margin
        elif partner_group in ['rxpartner']:
            final_df['partner_penny_margin'] = 0
            if 'partner_penny_fills_margin' in final_df.columns:
                log.info('setting partner_penny_margin')
                final_df['partner_penny_margin'] = final_df['partner_penny_fills_margin']
            if 'partner_penny_fills_margin_y' in final_df.columns:
                log.info('adjusting partner_penny_margin')
                final_df['partner_penny_margin'] = final_df.partner_penny_margin - final_df.partner_penny_fills_margin_y

            final_df['net_penny_fills'] = 0
            if 'penny_fills' in final_df.columns:
                log.info('setting net_penny_fills')
                final_df['net_penny_fills'] = final_df['penny_fills']
            if 'penny_fills_y' in final_df.columns:
                log.info('adjusting net_penny_fills')
                final_df['net_penny_fills'] = final_df.penny_fills - final_df.penny_fills_y

            final_df['partner_margin'] = (final_df['net_fills'] - final_df['net_penny_fills']) * rxpartner_constants.PARTNER_MARGIN_PER_CLAIM_USD
            final_df['partner_margin'] = final_df['partner_margin'] + final_df['partner_penny_margin']
            final_df['hippo_margin'] = final_df.net_margin - final_df.change_margin - final_df.erx_execution_costs - final_df.partner_margin
        elif partner_group in ['famulus']:
            final_df['non_otc_net_fills'] = final_df.non_otc_count - final_df.non_otc_count_y
            final_df['partner_margin'] = final_df['non_otc_net_fills'] * famulus_constants.PARTNER_MARGIN_PER_CLAIM_USD
            final_df['hippo_margin'] = final_df.net_margin - final_df.change_margin - final_df.erx_execution_costs - final_df.partner_margin
        elif partner_group in ['waltz']:
            final_df['net_wpr_fills'] = final_df.waltz_groupid_is_wpr - final_df.waltz_groupid_is_wpr_y # numer of claims we should pay $4 fee for Waltz - Customer Licensees 
            final_df['net_not_wpr_fills'] = final_df.net_fills - final_df.net_wpr_fills # numer of claims we should pay $3 fee for Waltz - Chain Pharmacy Licensees 
            final_df['partner_margin'] = (final_df['net_wpr_fills'] * waltz_constants.CUSTOMER_LICENSEES_MARGIN_USD) + (final_df['net_not_wpr_fills'] * waltz_constants.CHAIN_PHARMACY_LICENSEES_MARGIN_USD) # according to the Waltz contract we must pay $4 for all claims under Customer Licensees (group_id = 'WPR') and $3 for the rest
            final_df['hippo_margin'] = final_df.net_margin - final_df.change_margin - final_df.erx_execution_costs - final_df.partner_margin
        elif partner_group in ['Save.Health']:
            final_df['hippo_margin'] = final_df.net_margin - final_df.change_margin - final_df.erx_execution_costs - final_df.partner_margin
        elif partner_group in ['direct','wags_finder']:
            final_df['hippo_margin'] = final_df.net_margin - final_df.transaction_costs
        elif partner_group in ['cvs_tpdt']:
            date_condition = datetime.strptime(current_report_date, '%Y-%m-%d').date() >= datetime.strptime('2024-04-01', '%Y-%m-%d').date() # starting 2024-04-01 we start pay $0.10 Fee per Claim (CostVantage contract)
            final_df.loc[(final_df['contract_name'] == 'cvs_tpdt') & date_condition, 'partner_margin'] = final_df['net_fills'] * cvs_tpdt.COST_VANTAGE_PROCESSING_FEE
            final_df['hippo_margin'] = final_df.net_margin - final_df.transaction_costs - final_df.partner_margin
        elif partner_group in ['cvs_tpdm']:
            final_df['partner_margin'] = final_df['net_fills'] * cvs_tpdm.CVS_TPDM_PROCESSING_FEE
            final_df['hippo_margin'] = final_df.net_margin - final_df.transaction_costs - final_df.partner_margin
        elif partner_group in ['rxlink']:
            final_df['hippo_margin'] = final_df['net_margin'] * rxlink_constants.PARTNER_MARGIN_PER_CLAIM_HIPPO_PERCENT
            final_df['partner_margin'] = final_df['net_margin'] * rxlink_constants.PARTNER_MARGIN_PER_CLAIM_PARTNER_PERCENT 
        elif partner_group in ['Dr First']:
            final_df['hippo_margin'] = final_df['net_margin'] * rxinform_constants.PARTNER_MARGIN_PER_CLAIM_HIPPO_PERCENT
            final_df['partner_margin'] = final_df['net_margin'] * rxinform_constants.PARTNER_MARGIN_PER_CLAIM_PARTNER_PERCENT 
        elif partner_group in ['Rcopia']:
            final_df['hippo_margin'] = final_df['net_margin'] * rcopia_constants.PARTNER_MARGIN_PER_CLAIM_HIPPO_PERCENT
            final_df['partner_margin'] = final_df['net_margin'] * rcopia_constants.PARTNER_MARGIN_PER_CLAIM_PARTNER_PERCENT 
        else:
            raise ValueError(f'"{partner_group}" partner_group is not in the list of processable partner groups')
        final_df['margin_per_fill'] = final_df \
            .apply(lambda x: x.net_margin/x.net_fills if x.net_fills != Decimal('0') 
                else Decimal('0'), axis=1)
        final_df['new_user_fills'] = final_df.new_user_fills.fillna(0).astype('int64') - final_df.new_user_reversals.fillna(0).astype('int64')
        final_df['refills'] = final_df.returning_user_fills.fillna(0).astype('int64') - final_df.returning_user_reversals.fillna(0).astype('int64')

        final_df.loc[:,['net_fills','new_user_fills','returning_user_fills','reversals']] = final_df.loc[:,['net_fills','new_user_fills','returning_user_fills','reversals']].fillna(0).astype('int')
        final_df['hippo_margin_per_fill'] = final_df \
            .apply(lambda x: x.hippo_margin/x.net_fills if x.net_fills != Decimal('0') 
                else Decimal('0'), axis=1)

    elif partner_group == 'GoodRx':
        final_df['erx_execution_costs'] = final_df.execution_costs
        final_df['good_margin'] = final_df.good_margin - final_df.good_margin_y
        final_df['partner_margin'] = final_df['good_margin'].apply(lambda x: Decimal(x))
        final_df['hippo_margin'] = final_df.net_margin - final_df.transaction_costs - final_df.partner_margin
        final_df['margin_per_fill'] = final_df \
            .apply(lambda x: x.net_margin/x.net_fills if x.net_fills != Decimal('0') 
                else Decimal('0'), axis=1)    
        final_df['new_user_fills'] = final_df.new_user_fills.fillna(0) - final_df.new_user_reversals.fillna(0)
        final_df['refills'] = final_df.returning_user_fills.fillna(0) - final_df.returning_user_reversals.fillna(0)
        final_df.loc[:,['net_fills','new_user_fills','returning_user_fills','reversals']] = final_df.loc[:,['net_fills','new_user_fills','returning_user_fills','reversals']].astype('int')
        final_df['hippo_margin_per_fill'] = final_df \
            .apply(lambda x: x.hippo_margin/x.net_fills if x.net_fills != Decimal('0') 
                else Decimal('0'), axis=1)
        final_df.rename(columns={f'fill_{PERIOD_STR}':PERIOD_STR}, inplace = True)

    elif partner_group == 'webmd':
        final_df['negative_net_fills'] = -final_df['net_fills'].apply(lambda x: Decimal(x))
        final_df['net_revenue'] = final_df.hippo_net_revenue - final_df.hippo_net_revenue_y
        final_df['erx_execution_costs'] = final_df.execution_costs - final_df.execution_costs_y
        final_df['gross_profit'] = final_df.gross_profit - final_df.gross_profit_y
        final_df['net_penny_fills'] = (final_df.penny_fills - final_df.penny_fills_y).apply(lambda x: Decimal(x))
        final_df['net_penny_fill_profit'] = final_df.gross_penny_fill_profit - final_df.gross_penny_fill_profit_y
        final_df['fifty_pct_of_profit_over_15000'] = final_df.gross_profit_from_15000_onwards - final_df.gross_profit_from_15000_onwards_y

        final_df = agg_webmd_margin(final_df)
        final_df['hippo_margin'] = final_df.net_margin - final_df.change_margin - final_df.erx_execution_costs - final_df.partner_margin
        final_df['margin_per_fill'] = final_df \
            .apply(lambda x: x.net_margin/x.net_fills if x.net_fills != Decimal('0') 
                else Decimal('0'), axis=1)
        final_df['new_user_fills'] = final_df.new_user_fills.fillna(0).astype('int64') - final_df.new_user_reversals.fillna(0).astype('int64')
        final_df['refills'] = final_df.returning_user_fills.fillna(0).astype('int64') - final_df.returning_user_reversals.fillna(0).astype('int64')
        final_df.sort_values(by = f'fill_{PERIOD_STR}', ascending = False, inplace = True)
        final_df.loc[:,['net_fills','new_user_fills','returning_user_fills','reversals']] = final_df.loc[:,['net_fills','new_user_fills','returning_user_fills','reversals']].astype('int')
        final_df['hippo_margin_per_fill'] = final_df \
            .apply(lambda x: x.hippo_margin/x.net_fills if x.net_fills != Decimal('0') 
                else Decimal('0'), axis=1)

    final_df.loc[:,['hippo_margin','margin_per_fill','hippo_margin_per_fill','partner_margin', 'ingredient_cost_upside_usd', 'dispensing_fee_upside_usd']] = \
        final_df.loc[:,['hippo_margin','margin_per_fill','hippo_margin_per_fill','partner_margin', 'ingredient_cost_upside_usd', 'dispensing_fee_upside_usd']].astype('float').fillna(0).round(2)

    columns_to_modify = ['partner_margin', 'hippo_margin', 'ingredient_cost_upside_usd', 'dispensing_fee_upside_usd', 'hippo_margin_per_fill', 'margin_per_fill']
    # with this condition we set columns_to_modify values to zero for out of network and UNC fills
    zero_margin_condition = (final_df['contract_name'].str.strip() == 'out_of_network') | (final_df['sub_program_name'].str.endswith('unc')) | (final_df['reconciliation_program_annotation'].str.endswith('unc'))
    final_df.loc[zero_margin_condition, columns_to_modify] = 0

    # Add pbm_processing_fee_usd calculation
    final_df['pbm_processing_fee_usd'] = final_df['nrid'].apply(lambda x: calculate_pbm_fee(x))  # Assuming a function calculate_pbm_fee exists

    # Adjust partner_margin calculation to exclude pbm_processing_fee_usd
    final_df['partner_margin'] = final_df['partner_margin'] - final_df['pbm_processing_fee_usd']

    # Ensure hippo_margin is calculated correctly without pbm_processing_fee_usd
    final_df['hippo_margin'] = final_df.net_margin - final_df.change_margin - final_df.erx_execution_costs - final_df.partner_margin

    return final_df


def agg_webmd_margin(final_df):
    final_df_agg = final_df.sum(axis = 0).T

    if (final_df_agg['net_fills'] - final_df_agg['net_penny_fills']) <= 15000:    # check if the 15000 fills condition is met
        final_df['partner_margin'] = Decimal('4.5') * (final_df['net_fills'] - final_df['net_penny_fills'])
    else:
        final_df['partner_margin'] =  (Decimal('67500') / Decimal(len(final_df.chain_name.unique()))) + final_df['net_penny_fill_profit'] * Decimal('0.5') + max((final_df['gross_profit_from_15000_onwards'] - final_df['gross_profit_from_15000_onwards_y']) * Decimal('0.5'), ((final_df['net_fills'] - final_df['net_penny_fills']) - (Decimal('15000')/ Decimal(len(final_df.chain_name.unique())))) * Decimal('3.0'))
    
    return final_df
