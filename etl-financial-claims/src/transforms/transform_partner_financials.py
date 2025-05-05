import pandas as pd
import numpy as np
from decimal import *
from transforms import utils, pandas_helper
from transforms.chains import set_contract_and_program_goals
import sources.partners.string_constants as string_constants
from itertools import product
import ast

from hippo import logger

log = logger.getLogger('transform_partner_financials.py')

def process_current_period_data_per_chain(pcf_claims_df, rank_df, period, current_report_date, previous_start_date):
    pcf_claims_df[f'fill_{period}'] = pcf_claims_df.valid_from.dt.to_period(period[0].upper()).astype('datetime64[ns]')
    pcf_claims_df[f'reversal_{period}'] = pcf_claims_df.valid_to.dt.to_period(period[0].upper()).astype('datetime64[ns]')
    rank_df['min'] = rank_df['min'].dt.to_period(period[0].upper()).astype('datetime64[ns]')
    if period == 'day':
        pcf_claims_df = pcf_claims_df[(pcf_claims_df.valid_to >= (pcf_claims_df[f'fill_{period}'] + pd.DateOffset(days = 1)))] ## this allow me to have only the fills that at the end of that window were considered as actual fills net_fills_tx_count, those fills that were reversed in the next period will be let apart, no matter if they were made in the same or previous period
        pcf_claims_df = pcf_claims_df[(pcf_claims_df[f'fill_{period}']==f'{current_report_date}') | (pcf_claims_df[f'reversal_{period}']==f'{current_report_date}') | (pcf_claims_df[f'fill_{period}']==f'{previous_start_date}')] ## This will let apart fills/reversals from previous or next periods 
    elif period == 'week':
        pcf_claims_df = pcf_claims_df[(pcf_claims_df.valid_to >= (pcf_claims_df[f'fill_{period}'] + pd.DateOffset(weeks = 1)))] ## this allow me to have only the fills that at the end of that window were considered as actual fills net_fills_tx_count, those fills that were reversed in the next period will be let apart, no matter if they were made in the same or previous period
        pcf_claims_df = pcf_claims_df[(pcf_claims_df[f'fill_{period}']==f'{current_report_date}') | (pcf_claims_df[f'reversal_{period}']==f'{current_report_date}')| (pcf_claims_df[f'fill_{period}']==f'{previous_start_date}')] ## This will let apart fills/reversals from previous or next periods 

    elif period == 'month': 
        pcf_claims_df = pcf_claims_df[(pcf_claims_df.valid_to >= (pcf_claims_df[f'fill_{period}'] + pd.DateOffset(months=+1)))]
        pcf_claims_df = pcf_claims_df[(pcf_claims_df[f'fill_{period}']==f'{current_report_date}') | (pcf_claims_df[f'reversal_{period}']==f'{current_report_date}')| (pcf_claims_df[f'fill_{period}']==f'{previous_start_date}')]
    elif period == 'quarter': 
        pcf_claims_df = pcf_claims_df[(pcf_claims_df.valid_to >= (pcf_claims_df[f'fill_{period}'] + pd.DateOffset(months=+3)))]
        pcf_claims_df = pcf_claims_df[(pcf_claims_df[f'fill_{period}']==f'{current_report_date}') | (pcf_claims_df[f'reversal_{period}']==f'{current_report_date}')| (pcf_claims_df[f'fill_{period}']==f'{previous_start_date}')]
    else: 
        raise Exception('Time period different to "day", "week" or "month" and is not supported')
    return pcf_claims_df


def process_raw_claims(per_claim_fills_df, cpf_df, rank_df, phist_df, period, unique_partners_df):
    per_claim_fills_df = per_claim_fills_df.merge(cpf_df, how = 'left', on=['rx_id','valid_from'])
    per_claim_fills_df = pandas_helper.left_join_with_condition(per_claim_fills_df, phist_df, left_on='npi', right_on='id', filter_by = 'valid_from_x')
    per_claim_fills_df = per_claim_fills_df.merge(rank_df, how='left', left_on=['user',f'fill_{period}'], right_on=['user','min'])
    per_claim_fills_df['min'].fillna('returning', inplace = True)
    per_claim_fills_df['min'].where(per_claim_fills_df['min']=='returning', other='new', inplace = True)
    per_claim_fills_df.rename(columns={'min':'fill_type'}, inplace = True)

    # We need alias partner to differentiate real partners from reporting.carholders
    # from partner groups used to determine hippo vs. partner margin
    per_claim_fills_df['partner_group'] = per_claim_fills_df['partner'].cat.add_categories(['other','direct'])
    per_claim_fills_df['partner_group'].replace(string_constants.DIRECT_PARTNER, 'direct', inplace = True)
    per_claim_fills_df.loc[~per_claim_fills_df['partner_group'].isin(string_constants.PARTNER_GROUPS_EXCLUDED_FROM_OTHER), 'partner_group'] = 'other'
    per_claim_fills_df.partner.cat.remove_unused_categories(inplace = True)
    per_claim_fills_df['net_revenue'] = per_claim_fills_df.patient_pay_resp
    per_claim_fills_df['net_drug_costs'] = per_claim_fills_df.drug_cost
    per_claim_fills_df['unc'] = per_claim_fills_df.usual_and_customary_charge
    per_claim_fills_df['margin'] = -per_claim_fills_df.total_paid_response
    per_claim_fills_df['erx_cost'] = per_claim_fills_df.erx_fee
    per_claim_fills_df['processor_fee'] = per_claim_fills_df.processor_fee
    per_claim_fills_df['change_margin'] = per_claim_fills_df.pbm_fee
    per_claim_fills_df['ingredient_cost_paid_resp_dollars'] = per_claim_fills_df.ingredient_cost_paid_resp
    per_claim_fills_df['dispensing_fee_paid_resp_dollars'] = per_claim_fills_df.dispensing_fee_paid_resp
    per_claim_fills_df = utils.cast_cents_to_dollars(per_claim_fills_df, column_names=['net_revenue','net_drug_costs','unc','margin','erx_cost','processor_fee','change_margin','ingredient_cost_paid_resp_dollars','dispensing_fee_paid_resp_dollars'])
    per_claim_fills_df['ig'] = per_claim_fills_df.ingredient_cost_paid_resp_dollars + per_claim_fills_df.margin + per_claim_fills_df.dispensing_fee_paid_resp_dollars
    per_claim_fills_df['fill_month'] = per_claim_fills_df[f'fill_{period}'].dt.to_period('M').astype('datetime64[ns]')
    per_claim_fills_df['reversal_month'] = per_claim_fills_df[f'reversal_{period}'].dt.to_period('M').astype('datetime64[ns]')
    per_claim_fills_df['partner_group'] = per_claim_fills_df['partner_group'].astype('object')

    return per_claim_fills_df

def process_raw_partner_dataframes(per_claim_fills_df, partner, current_report_date, period):
    per_partner_claim_fills_df = per_claim_fills_df.copy()
    per_partner_claim_fills_df = per_partner_claim_fills_df[per_partner_claim_fills_df['partner']==partner].drop_duplicates().reset_index(drop = True)
    per_partner_claim_fills_df = per_partner_claim_fills_df[(per_partner_claim_fills_df[f'fill_{period}']==f'{current_report_date}') | (per_partner_claim_fills_df[f'reversal_{period}']==f'{current_report_date}')]

    per_partner_claim_fills_df['new'] = (per_partner_claim_fills_df['fill_type'] == 'new').astype(bool)
    per_partner_claim_fills_df['returning'] = (per_partner_claim_fills_df['fill_type'] == 'returning').astype(bool)

    per_partner_claim_fills_df['new_returning_flag'] = per_partner_claim_fills_df['fill_type']

    return per_partner_claim_fills_df

def _check_dates_reliability(final_df, last_period_df, period, previous_report_date, partner_financials_bucket):
    """
    this function compares previous period date and current period date to avoid diff more than one period
    the only exclusion - if there is no file to download from the previous period and default file was downloaded (last period date == '2050-01-01')
    """
    exception_string = 'partner_financials_{}.csv contain dates different to previous report period! Check the file in s3://{}/exports/last_period/'.format(previous_report_date, partner_financials_bucket)
    if period == 'month' and final_df[period].max() != last_period_df[period].max() + pd.DateOffset(months = +1) and last_period_df[period].max() != pd.to_datetime('2050-01-01'):
        raise Exception(exception_string)
    elif period == 'week' and (final_df[period].max() != last_period_df[period].max() + pd.DateOffset(weeks=+1)) and last_period_df[period].max() != pd.to_datetime('2050-01-01'):
        raise Exception(exception_string)

def calculate_contracted_elements(claims, current_report_date, source_dict_current_contracts={}, dict_conditions_per_contract_program = {}, dict_ndcs_per_contract_program = {}):
    # transform cents to usd
    claims = claims.copy()

    claims.loc[:, 'ingredient_cost_usd'] = (claims['ingredient_cost_paid_resp'] / 100).astype(float)
    claims.loc[:, 'dispensing_fee_usd'] = (claims['dispensing_fee_paid_resp'] / 100).astype(float)
    claims.loc[:, 'margin_usd'] = -(claims['total_paid_response'] / 100).astype(float)
    claims.loc[:, 'product_id'] = claims['product_id'].apply(lambda x: str(x).zfill(11))

    
    # We need to process out of network contract last to make sure it's used with special fallback mask
    for contract, programs in source_dict_current_contracts.items():
        if contract == 'out_of_network':
            continue 

        log.info("processing contract %s", contract)    
        for program, contract_dictionary in programs.items():
            log.info("processing program %s", program)

            claims = _process_program(claims, source_dict_current_contracts, dict_conditions_per_contract_program, dict_ndcs_per_contract_program, contract_dictionary['formulas'], current_report_date, contract, program)

    for contract, programs in source_dict_current_contracts.items():
        if contract != 'out_of_network':
            continue 

        log.info("processing contract %s", contract)
        for program, contract_dictionary in programs.items():
            log.info("processing program %s", program)

            claims = _process_program(claims, source_dict_current_contracts, dict_conditions_per_contract_program, dict_ndcs_per_contract_program, contract_dictionary['formulas'], current_report_date, contract, program)
    

    try:
        # Filter rows where chain_name is in the specified list
        claims.loc[:,'ingredient_cost_upside_usd'].fillna(0, inplace=True)
        claims.loc[:,'dispensing_fee_upside_usd'].fillna(0, inplace=True)
        claims.loc[:, 'margin_upside_usd'].fillna(0, inplace=True)

        # Convert certain columns to Decimal
    except:
        claims['ingredient_cost_upside_usd'] = 0
        claims['dispensing_fee_upside_usd'] = 0
        claims['margin_upside_usd'] = 0

    columns_to_parse = ['ingredient_cost_upside_usd', 'dispensing_fee_upside_usd', 'margin_upside_usd']
    for col in columns_to_parse:
        claims[col] = claims[col].apply(Decimal)

    return claims[['partner_group', 'contract_name', 'program_name', 'sub_program_name', 'reconciliation_program','reconciliation_program_annotation', 'brand_generic_flag', 'ingredient_cost_upside_usd', 'dispensing_fee_upside_usd', 'margin_upside_usd']]


def join_mac_cost(claims_df, partner, source_dict_current_contracts, dict_conditions_per_contract_program, dict_ndcs_per_contract_program, dict_mac_per_contract_program):
    claims = claims_df.copy()
    
    for contract, programs in source_dict_current_contracts.items():
        if contract == 'out_of_network':
            continue 

        log.info("processing contract %s", contract)    
        for program, contract_dictionary in programs.items():
            log.info("processing program %s", program)

            contract_condition_df = dict_conditions_per_contract_program[contract][program]
            ndc_df = dict_ndcs_per_contract_program[contract][program]
            mac_df = dict_mac_per_contract_program[contract][program]

            bin_number_list = contract_condition_df['bin_number'][0]
            chain_codes_list = ast.literal_eval(contract_condition_df['chain_codes'][0])

            filtered_claims = pandas_helper.left_join_with_condition_preserve_index(claims, ndc_df, left_on='product_id', right_on='ndc')
            
            ## Filter corresponding claims per contract/program
            ## Rest of contracts/programs
            if contract == 'out_of_network':
                mask = (pd.isnull(filtered_claims['contract_name'])) 
            
            elif contract == 'change_healthcare':
                # Change Healthcare went down as of 22.02.2024
                mask = (filtered_claims['bin_number'].isin(bin_number_list)) & (filtered_claims['chain_code'].isin(chain_codes_list)) & (pd.notnull(filtered_claims['ndc'])) & (filtered_claims['claim_date_of_service'] <= pd.to_datetime('2024-02-22'))

            elif 'network_reimbursement_id_exclude_flag' in contract_condition_df.columns.to_list():
                network_reimbursement_id_list = ast.literal_eval(contract_condition_df['network_reimbursement_id'][0])

                if contract_condition_df['network_reimbursement_id_exclude_flag'][0].lower() == 'true':
                    ## All claims with network reimbursement_id NOT 8379 belongs to hippo_cvs contract
                    mask = (filtered_claims['bin_number'].isin(bin_number_list)) & (~filtered_claims['network_reimbursement_id'].isin(network_reimbursement_id_list)) & (filtered_claims['chain_code'].isin(chain_codes_list)) & (pd.notnull(filtered_claims['ndc'])) 
                                    
                else:
                    ## All claims with network reimbursement_id 8379 belongs to hippo_cvs_webmd contract
                    mask = (filtered_claims['bin_number'].isin(bin_number_list)) & (filtered_claims['network_reimbursement_id'].isin(network_reimbursement_id_list)) & (filtered_claims['chain_code'].isin(chain_codes_list)) & (pd.notnull(filtered_claims['ndc'])) 
            else:
                mask = (filtered_claims['bin_number'].isin(bin_number_list)) & (filtered_claims['chain_code'].isin(chain_codes_list)) & (pd.notnull(filtered_claims['ndc'])) 
            

            if claims.loc[mask].shape[0] != 0:
                claims.loc[mask, 'mac'] = pandas_helper.left_join_with_condition_preserve_index(claims.loc[mask].drop(columns='mac', errors='ignore'), mac_df, left_on='product_id', right_on='mac_ndc').drop(columns=['mac_ndc'])['mac']
            else:
                claims.loc[mask,'mac'] = np.nan

    return claims['mac']

def _process_program(claims, source_dict_current_contracts, dict_conditions_per_contract_program, dict_ndcs_per_contract_program, contract_dictionary, current_report_date, contract, program):
    claims = claims.copy()
    ## Contract conditions
    contract_condition_df = dict_conditions_per_contract_program[contract][program]
    ndc_df = dict_ndcs_per_contract_program[contract][program]
    bin_number_list = contract_condition_df['bin_number'][0]
    chain_codes_list = ast.literal_eval(contract_condition_df['chain_codes'][0])

    filtered_claims = pandas_helper.left_join_with_condition_preserve_index(claims, ndc_df, left_on='product_id', right_on='ndc')
    
    ## Filter corresponding claims per contract/program
    ## Rest of contracts/programs
    if contract == 'out_of_network':
        mask = (pd.isnull(filtered_claims['contract_name'])) 
    
    elif contract == 'change_healthcare':
        # Change Healthcare went down as of 22.02.2024
        mask = (filtered_claims['bin_number'].isin(bin_number_list)) & (filtered_claims['chain_code'].isin(chain_codes_list)) & (pd.notnull(filtered_claims['ndc'])) & (filtered_claims['claim_date_of_service'] <= pd.to_datetime('2024-02-22'))

    elif 'network_reimbursement_id_exclude_flag' in contract_condition_df.columns.to_list():
        network_reimbursement_id_list = ast.literal_eval(contract_condition_df['network_reimbursement_id'][0])

        if contract_condition_df['network_reimbursement_id_exclude_flag'][0].lower() == 'true':
            ## All claims with network reimbursement_id NOT 8379 belongs to hippo_cvs contract
            mask = (filtered_claims['bin_number'].isin(bin_number_list)) & (~filtered_claims['network_reimbursement_id'].isin(network_reimbursement_id_list)) & (filtered_claims['chain_code'].isin(chain_codes_list)) & (pd.notnull(filtered_claims['ndc'])) 
                            
        else:
            ## All claims with network reimbursement_id 8379 belongs to hippo_cvs_webmd contract
            mask = (filtered_claims['bin_number'].isin(bin_number_list)) & (filtered_claims['network_reimbursement_id'].isin(network_reimbursement_id_list)) & (filtered_claims['chain_code'].isin(chain_codes_list)) & (pd.notnull(filtered_claims['ndc'])) 
    else:
        mask = (filtered_claims['bin_number'].isin(bin_number_list)) & (filtered_claims['chain_code'].isin(chain_codes_list)) & (pd.notnull(filtered_claims['ndc'])) 
    

    ingredient_cost_upside_allowed_str = contract_condition_df['ingredient_cost_upside_allowed'][0]
    dispensing_fee_upside_allowed_str = contract_condition_df['dispensing_fee_upside_allowed'][0]
    average_admin_fee_allowed_str = contract_condition_df['average_admin_fee_allowed'][0]

    if claims.loc[mask].shape[0] != 0:
        result = source_dict_current_contracts[contract][program]['drug_type'](claims[mask])
    
        # Print the shape of the result to ensure it matches
        claims.loc[mask, 'brand_generic_flag'] = result
        log.info("Added brand_generic_flag shape: %s", claims.loc[mask].shape)
        log.info("Nullable rest brand_generic_flag shape: %s", claims.loc[pd.isnull(claims['brand_generic_flag'])].shape)
    else:
        claims.loc[mask,'brand_generic_flag'] = pd.Series(dtype=object)

    update_columns = ['contract_name', 'program_name', 'sub_program_name', 'reconciliation_program', 'reconciliation_program_annotation', 'contracted_ingredient_cost_usd', 'contracted_dispensing_fee_usd', 'contracted_margin_usd']
    temp_upside_df = set_contract_and_program_goals.calculate_contracted_elements(claims.loc[mask], contract_dictionary)     
    claims.loc[mask, update_columns] = temp_upside_df[update_columns]

    # log.info("Updated claims count: %s", len(claims.loc[mask]))
    
    if len(mask) != 0:
        if ingredient_cost_upside_allowed_str.lower() == 'true':
            claims.loc[mask,'ingredient_cost_upside_usd'] = claims.loc[mask,'ingredient_cost_usd'] - claims.loc[mask,'contracted_ingredient_cost_usd']
        else:
            claims.loc[mask,'ingredient_cost_upside_usd'] = 0
            
        if dispensing_fee_upside_allowed_str.lower() == 'true':
            claims.loc[mask,'dispensing_fee_upside_usd'] = claims.loc[mask,'dispensing_fee_usd'] - claims.loc[mask,'contracted_dispensing_fee_usd']
        else:
            claims.loc[mask,'ingredient_dispensing_fee_usd'] = 0

        if average_admin_fee_allowed_str.lower() == 'true':
            claims.loc[mask,'margin_upside_usd'] = claims.loc[mask,'contracted_margin_usd'] - claims.loc[mask,'margin_usd']
        else:
            claims.loc[mask,'margin_upside_usd'] = 0
    else:
        claims.loc[mask,'ingredient_cost_upside_usd'] = pd.Series(dtype='float64')
        claims.loc[mask,'ingredient_dispensing_fee_usd'] = pd.Series(dtype='float64')
        claims.loc[mask,'margin_upside_usd'] = pd.Series(dtype='float64')

    return claims
