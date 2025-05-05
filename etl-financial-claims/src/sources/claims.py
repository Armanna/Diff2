import pandas as pd
import numpy as np
from decimal import Decimal
from datetime import datetime
from transforms import utils
from decimal import Decimal
import ast

from hippo import logger

from sources.chains.other_chains import other_chains

log = logger.getLogger('claims.py')

def process_claims(claims_df):
   """
   this function used to process claims downloaded with etl-lib claims downloader
   """
   claims_df['valid_to'] = claims_df['valid_to'].astype(str)
   claims_df['valid_to'].replace('2300-01-01 00:00:00', '2050-01-01 00:00:00', inplace=True)
   claims_df['valid_to'] = pd.to_datetime(claims_df['valid_to'],format='%Y-%m-%d %H:%M:%S')
   claims_df['valid_from'] = pd.to_datetime(claims_df['valid_from'],format='%Y-%m-%d %H:%M:%S')
   claims_df['basis_of_reimbursement_determination_resp'] = claims_df['basis_of_reimbursement_determination_resp'].astype('category')
   claims_df['dispense_as_written'] = claims_df['dispense_as_written'].astype('category')
   claims_df['npi'] = claims_df['npi'].astype('int64')
   claims_df['product_id'] = claims_df['product_id'].astype(str).str.zfill(11)
   claims_df['days_supply'] = claims_df['days_supply'].fillna(0).astype('int64')
   claims_df['quantity_dispensed'] = claims_df['quantity_dispensed'].fillna(0).astype('float64')
   claims_df = utils.cast_columns_to_decimal(claims_df, column_names=['patient_pay_resp','drug_cost','total_paid_response','ingredient_cost_paid_resp','dispensing_fee_paid_resp','usual_and_customary_charge'], fillna_flag = True)
   claims_df['user'] = claims_df['first_name'] + claims_df['last_name'] + claims_df['date_of_birth']
   claims_df['partner'] = claims_df['partner'].astype('category')
   claims_df['bin_number'] = claims_df['bin_number'].astype('category')
   claims_df['claim_date_of_service'] = pd.to_datetime(claims_df['claim_date_of_service'],format='%Y-%m-%d %H:%M:%S') + pd.Timedelta(hours=12)

   return claims_df[['user', 'npi', 'valid_from', 'valid_to', 'basis_of_reimbursement_determination_resp', 'rx_id','usual_and_customary_charge','patient_pay_resp','drug_cost','total_paid_response','cardholder_id','n_cardholder_id','product_id','ingredient_cost_paid_resp','dispensing_fee_paid_resp','partner','dispense_as_written', 'network_reimbursement_id', 'bin_number','claim_date_of_service', 'quantity_dispensed', 'days_supply','group_id']]


def brand_generic_indicator(df, column_name = 'brand_generic_flag', source_dict_current_contracts = {}, dict_conditions_per_contract_program = {}):
    log.info("contracts list shape before: %s", df.shape)
    for contract, programs in source_dict_current_contracts.items():
        log.info("brand_generic contract: %s", contract)
        for program, brand_generic_func in programs.items():
            ## Contract conditions
            log.info("brand_generic program: %s", program)

            contract_condition_df = dict_conditions_per_contract_program[contract][program]
            bin_number_list = contract_condition_df['bin_number'][0]
            chain_codes_list = ast.literal_eval(contract_condition_df['chain_codes'][0])

            ## Filter corresponding claims per contract/program
            if 'network_reimbursement_id_exclude_flag' in contract_condition_df.columns.to_list():
                network_reimbursement_id_list = ast.literal_eval(contract_condition_df['network_reimbursement_id'][0])
                if contract_condition_df['network_reimbursement_id_exclude_flag'][0].lower() == 'true':
                    mask = (df['bin_number'].isin(bin_number_list)) & (~df['network_reimbursement_id'].isin(network_reimbursement_id_list)) & (df['chain_code'].isin(chain_codes_list))
                                    
                else:
                    mask = (df['bin_number'].isin(bin_number_list)) & (df['network_reimbursement_id'].isin(network_reimbursement_id_list)) & (df['chain_code'].isin(chain_codes_list))
                
            else:
                ## Rest of contracts/programs
                mask = (df['bin_number'].isin(bin_number_list)) & (df['chain_code'].isin(chain_codes_list))

            log.info("Updating claims shape: %s", df.loc[mask].shape)
            df.loc[mask, column_name] = brand_generic_func(df[mask])
            # df.loc[mask, column_name] = df.loc[mask].apply(brand_generic_func, axis=1)

    mask = pd.isnull(df[column_name])
    log.info("not in the contracts list shape after: %s", df.loc[mask].shape)
    df.loc[mask, column_name] = other_chains.brand_generic_indicator_other_chains_vectorized(df[mask])
    # df.loc[mask, column_name] = df.loc[mask].apply(other_chains.brand_generic_indicator_other_chains, axis=1)

    return df[[column_name]]

def fills_reversals_indicator(df, period_start, period_end, valid_from_column='valid_from', valid_to_column='valid_to'):
  period_start = datetime.strptime(period_start, '%Y-%m-%d')
  period_end = datetime.strptime(period_end, '%Y-%m-%d')
  df['fill_reversal_indicator'] = np.where(
                                            (df[valid_from_column].dt.date >= period_start.date()) 
                                                &
                                            (df[valid_from_column].dt.date <= period_end.date())
                                                &
                                            (df[valid_to_column].dt.date > period_end.date()), 
                                                Decimal(1),   ## net_fills_tx_count
                                            np.where(
                                                (df[valid_from_column].dt.date < period_start.date())
                                                    &
                                                (df[valid_to_column].dt.date <= period_end.date())
                                                    &
                                                (df[valid_to_column].dt.date >= period_start.date()), 
                                                    Decimal(-1), 
                                                        None))
  return df[['fill_reversal_indicator']]
