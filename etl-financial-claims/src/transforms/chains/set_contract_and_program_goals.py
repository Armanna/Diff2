import pandas as pd
import numpy as np
import re

from hippo import logger

log = logger.getLogger('set_contract_and_program_goals.py')

def calculate_contracted_elements(claims_df, contract_dictionary):

    ## Conditions will be loaded from constant file and each string statement will generate its respective condition
    ## Values
    # log.info("contract dictionary is: %s", contract_dictionary)
    unique_partners = claims_df['partner'].unique()
    unique_partners_str = ', '.join(map(str, unique_partners))
    # log.info("processing partner: %s", unique_partners_str)
    # log.info("full contract shape: %s", claims_df.shape)

    partner_full_claims_list_df = pd.DataFrame({})
    contract_name = contract_dictionary['contract_name']
    program_name = contract_dictionary['program_name']

    if claims_df.shape[0] == 0:
        return _return_empty_values(partner_full_claims_list_df, contract_name, program_name)
    
    for historical_set in contract_dictionary['historical_sets']:
        # log.info("claims_df shape: %s", claims_df.shape)
        historical_set_claims_df = claims_df[(claims_df['claim_date_of_service'] > historical_set['valid_from']) & (claims_df['claim_date_of_service'] <= historical_set['valid_to'])]

        historical_set_name = historical_set['name']
        # log.info("processing historical_set_name: %s", historical_set_name)
        # log.info("historical_set: %s", historical_set)
        # log.info("historical_set_claims_df shape: %s", historical_set_claims_df.shape)

        if historical_set_claims_df.shape[0] == 0:
            continue

        claims_subsets_df = pd.DataFrame({})

        for sub_program in historical_set['dict_constants']['sub_programs']:
            # log.info("sub_program: %s", sub_program)

            for sub_program_key, sub_program_value in sub_program.items():
                # log.info("sub_program_key: %s", sub_program_key)
                # log.info("sub_program_value: %s", sub_program_value)

                try:
                    contract_margin = sub_program_value['MARGIN']
                except:
                    # some sub_programs, like UNC, not always define MARGIN as target
                    contract_margin = 0
                # log.info("contract_margin: %s", contract_margin)

                sub_program_name = historical_set_name + '<>' + sub_program_key

                for reconciliation_program_key, reconciliation_program_values in sub_program_value.items():
                    claims_subset_df = pd.DataFrame({})

                    # log.info("reconciliation_program_key: %s", reconciliation_program_key)
                    # log.info("reconciliation_program_value: %s", reconciliation_program_values)

                    if isinstance(reconciliation_program_values, list):
                        for reconciliation_annotated_program in reconciliation_program_values:
                            # log.info("reconciliation_annotated_program: %s", reconciliation_annotated_program)
                            claim_condition = _add_basis_of_reimbursement(reconciliation_annotated_program['condition'], reconciliation_annotated_program['base'])
                            # log.info("claim condition: %s", claim_condition)

                            claims_subset_df = historical_set_claims_df.query(claim_condition).copy()
                            # log.info("claim subset_df shape: %s", claims_subset_df.shape)
                            if claims_subset_df.shape[0] == 0:
                                continue
                            else:
                                # log.info("reconciliation_annotated_program subset shape: %s", claims_subset_df.shape)
                                claims_subset_df =_calculate_contract_variables(claims_subset_df, contract_name, contract_margin, reconciliation_annotated_program, program_name, sub_program_name, reconciliation_program_key, reconciliation_annotated_program['name'])
                            
                            # log.info("claim subset_df shape after calculation: %s", claims_subset_df.shape)

                            claims_subsets_df = pd.concat([claims_subsets_df, claims_subset_df])
                    
                    if isinstance(reconciliation_program_values, dict):
                        # log.info("reconciliation_annotated_program: %s", reconciliation_program_values)                    
                        claim_condition = _add_basis_of_reimbursement(reconciliation_program_values['condition'], reconciliation_program_values['base'])
                        # log.info("claim condition: %s", claim_condition)

                        claims_subset_df = historical_set_claims_df.query(claim_condition).copy()
                        # log.info("claim subset_df shape: %s", claims_subset_df.shape)
                        if claims_subset_df.shape[0] == 0:
                            continue
                        else:
                            # log.info("reconciliation_annotated_program subset shape: %s", claims_subset_df.shape)
                            claims_subset_df = _calculate_contract_variables(claims_subset_df, contract_name, contract_margin, reconciliation_program_values, program_name, sub_program_name, reconciliation_program_key, reconciliation_program_key)

                        # log.info("claim subset_df shape after calculation: %s", claims_subset_df.shape)
                    
                        claims_subsets_df = pd.concat([claims_subsets_df, claims_subset_df])

        if claims_subsets_df.shape[0] == 0:
            claims_subsets_df = _return_empty_values(claims_subsets_df, contract_name, program_name, sub_program_name)

        if claims_subsets_df.shape[0] != historical_set_claims_df.shape[0]:
            if claims_subsets_df.shape[0] != 0:
                claim_identification_columns = ['bin_number', 'chain_name', 'product_id', 'valid_from', 'valid_to', 'usual_and_customary_charge', 'partner']

                # log.info("Some claims missing it's programs")
                # log.info("historical_set_claims_df shape: %s", historical_set_claims_df.shape)
                # log.info("claims_subsets_df shape: %s", claims_subsets_df.shape)
                merged_df = pd.merge(historical_set_claims_df, claims_subsets_df, 
                            on=claim_identification_columns,
                            how='outer', 
                            indicator=True)
                
                # Rows unique to historical_set_claims_df
                unique_to_historical_set_claims_df = merged_df[merged_df['_merge'] == 'left_only']
                # log.info("Rows unique to original claims: %s", unique_to_historical_set_claims_df)

                # Rows unique to claims_subsets_df
                unique_to_claims_subsets_df = merged_df[merged_df['_merge'] == 'right_only']
                # log.info("Rows unique to program claims: %s", unique_to_claims_subsets_df)

                # Rows duplicated within claims_subsets_df
                duplicated_df =  unique_to_claims_subsets_df[unique_to_claims_subsets_df.duplicated(subset=claim_identification_columns)]
                # log.info("Rows duplicated to program claims: %s", duplicated_df)

        # assert claims_subsets_df.shape[0] == claims_df.shape[0], "Some claims are missing its program. Subset rows: {}, Original rows: {}".format(claims_subsets_df.shape[0], claims_df.shape[0])

        partner_full_claims_list_df = pd.concat([partner_full_claims_list_df, claims_subsets_df])

    if partner_full_claims_list_df[partner_full_claims_list_df.index.duplicated()].shape[0] == 0:
        assert partner_full_claims_list_df[partner_full_claims_list_df.index.duplicated()].shape[0] == 0, "Some claims are duplicated across programs"

    if partner_full_claims_list_df.shape[0] == 0:
        # Rare case when contract has few claims but none of them can match a program/contract
        return _return_empty_values(partner_full_claims_list_df, contract_name, program_name)

    return partner_full_claims_list_df[
        ['contract_name', 'program_name', 'sub_program_name', 'reconciliation_program', 'reconciliation_program_annotation', 'contracted_ingredient_cost_usd', 'contracted_dispensing_fee_usd', 'contracted_margin_usd']
    ]

def _calculate_contract_variables(df, contract_name, contract_margin, program_values, program_name, sub_program_name, reconciliation_program, reconciliation_program_annotation):
    if df.shape[0] > 0:
        df.loc[:, 'contract_name'] = contract_name
        df.loc[:, 'program_name'] = program_name
        df.loc[:, 'sub_program_name'] = sub_program_name
        df.loc[:, 'reconciliation_program'] = reconciliation_program
        df.loc[:, 'reconciliation_program_annotation'] = reconciliation_program_annotation
    else:
        return df

    if sub_program_name.endswith('unc') or contract_name in ['change_healthcare', 'out_of_network']:
        df['contracted_ingredient_cost_usd'] = 0
        df['contracted_dispensing_fee_usd'] = 0
        df['contracted_margin_usd'] = 0

        return df

    if program_values['base'] == 'AWP':
        df['contracted_ingredient_cost_usd'] = (df['awp'] / 100) * df['quantity_dispensed'] * (1 - program_values['value'])
    elif program_values['base'] == 'NADAC':
        base_value = np.where(df['nadac'].notna(), df['nadac'], df['gpi_nadac'])
        df['contracted_ingredient_cost_usd'] = (base_value / 100) * df['quantity_dispensed'] * (1 - program_values['value'])
    elif program_values['base'] == 'WAC':
        df['contracted_ingredient_cost_usd'] = (df['wac'] / 100) * df['quantity_dispensed'] * (1 - program_values['value'])
    elif program_values['base'] == 'MAC':
        df['contracted_ingredient_cost_usd'] = (df['mac'] / 100) * df['quantity_dispensed'] * (1 - program_values['value'])
    else:
        raise ValueError('Cost Base not supported')

    df.loc[:, 'contracted_dispensing_fee_usd'] = program_values['DISP_FEE']
    df.loc[:, 'contracted_margin_usd'] = contract_margin

    return df

def _add_basis_of_reimbursement(source_condition, cost_base):
    base_condition = '00'

    formatted_condition = _format_for_query(source_condition)

    if cost_base == 'AWP':
        base_condition = '03'
    elif cost_base == 'NADAC':
        base_condition = '20'
    elif cost_base == 'WAC':
        base_condition = '13'
    elif cost_base == 'MAC':
        base_condition = '07'
    elif cost_base == 'UNC':
        base_condition = '04'
    else:
        raise ValueError('Base condition unknown')

    return "{formatted_condition} & (basis_of_reimbursement_determination_resp == '{base_condition}')".format(formatted_condition=formatted_condition, base_condition=base_condition)

def _format_for_query(source_condition):
    # Regular expression to find all instances of claims['column_name']
    pattern = r"claims\['(.*?)'\]"
    # Replace matched patterns with just the column name
    formatted_str = re.sub(pattern, r'\1', source_condition)
    return formatted_str

def _return_empty_values(df, contract_name, program_name, sub_program_name = None):
    df['contracted_ingredient_cost_usd'] = 0
    df['contracted_dispensing_fee_usd'] = 0
    df['contracted_margin_usd'] = 0
    df['contract_name'] = contract_name
    df['program_name'] = program_name
    df['sub_program_name'] = sub_program_name
    df['reconciliation_program'] = None
    df['reconciliation_program_annotation'] = None
    df['contracted_ingredient_cost_usd'] = 0
    df['contracted_dispensing_fee_usd'] = 0
    df['contracted_margin_usd'] = 0

    return df
