import sources.s3 as s3
import datetime as dt
import pandas as pd
from datetime import datetime

from hippo import logger

from sources.chains.contract_program_mapping import extract_start_end_contract_dates
from transforms.utils import convert_to_list

log = logger.getLogger('pull_etl_pbm_hippo_files')

def pull_exported_hippo_pbm_file(current_report_date='',pbm_hippo_bucket='',pbm_hippo_export_prefix='',pbm_hippo_file_name='', dict_current_etl_pbm_hippo_contracts={}):
    dict_files_program = {}
    for contract, programs in dict_current_etl_pbm_hippo_contracts.items():
        if pbm_hippo_file_name != 'mac' and contract in ['change_healthcare', 'out_of_network']:
            log.info("Files for change healthcare and out_of_network are manual. Skipping")
            continue

        dict_programs_condition = {}
        for program, program_attributes in programs.items(): ## Iterate over each program of the contract
            contract_start_date, contract_end_date = extract_start_end_contract_dates(program_attributes)

            if pbm_hippo_file_name in ['contract_claims_conditions']: ## Particular program/contract that does not have excluded_ndcs exported file
                if (contract in ['cvs_tpdt','walmart']) and (program in ['specialty_list','four_dollar_list']) and (pbm_hippo_file_name == 'excluded_ndcs'):  ## Particular program/contract that does not have excluded_ndcs exported file
                    dict_programs_condition[program] = pd.DataFrame(columns = ['ndc', 'chain_name', 'reason'])
                    continue

                if datetime.strptime(current_report_date, "%Y-%m-%d") < contract_start_date:
                    report_date = contract_start_date.strftime("%Y.%m.%d") # we can do this for future as a matter of exception. claim_date_of_service will still filter claims properly.
                elif datetime.strptime(current_report_date, "%Y-%m-%d") > contract_end_date:
                    report_date = contract_end_date.strftime("%Y.%m.%d")
                else:
                    report_date = current_report_date
                
                contract_file_path = f'{contract}/{program}/{report_date.replace("-",".")}/{pbm_hippo_file_name}'
                log.info(f'Trying to download {contract_file_path} file')
                dict_programs_condition[program] = s3.PartnerFinancialsS3Downloader(pbm_hippo_bucket, pbm_hippo_export_prefix, contract_file_path).pull()[0]
                dict_programs_condition[program]['bin_number'] = dict_programs_condition[program]['bin_number'].apply(convert_to_list)

                mapping_col_dict = {'id': 'ndc'}
                dict_programs_condition[program] = dict_programs_condition[program].rename(columns = mapping_col_dict)

                log.info("Loading files for contract %s", contract)
                log.info("Loading files for program %s", program)
                log.info("The shape is %s", dict_programs_condition[program].shape)
            else:
                dict_programs_condition[program] = pull_exported_historic_hippo_pbm_file(pbm_hippo_bucket, pbm_hippo_export_prefix, contract, program, pbm_hippo_file_name)
            
        dict_files_program[contract] = dict_programs_condition

    return dict_files_program


def pull_exported_historic_hippo_pbm_file(pbm_hippo_bucket, pbm_hippo_export_prefix, contract, program, pbm_hippo_file_name):
    history_prefix = f'{pbm_hippo_export_prefix}{contract}/{program}/history'

    if pbm_hippo_file_name == 'mac':
        try:
            pbm_hippo_historic_df = s3.PartnerFinancialsS3Downloader(pbm_hippo_bucket, history_prefix, pbm_hippo_file_name).pull()[0]
        except FileNotFoundError:
            log.info(f"MAC history file not found in {pbm_hippo_bucket}/{history_prefix}.")
            return pd.DataFrame(columns=['mac_ndc', 'mac', 'valid_from', 'valid_to'])
    else:
        pbm_hippo_historic_df = s3.PartnerFinancialsS3Downloader(pbm_hippo_bucket, history_prefix, pbm_hippo_file_name).pull()[0]

    end_date_mapping_dict = {
        '2300.01.01T00:00:00': '2050.01.01T00:00:00'
    }

    if 'ndc' in pbm_hippo_historic_df.columns.tolist():
        pbm_hippo_historic_df['ndc'] = pbm_hippo_historic_df['ndc'].astype(str).str.zfill(11)

    pbm_hippo_historic_df['valid_to'] = pbm_hippo_historic_df['valid_to'].replace(end_date_mapping_dict)
    pbm_hippo_historic_df['valid_from'] = pd.to_datetime(pbm_hippo_historic_df['valid_from'], format="%Y.%m.%dT%H:%M:%S")
    pbm_hippo_historic_df['valid_to'] = pd.to_datetime(pbm_hippo_historic_df['valid_to'], format="%Y.%m.%dT%H:%M:%S")
    
    if pbm_hippo_file_name == 'mac':
        pbm_hippo_historic_df['unit_cost'] = pbm_hippo_historic_df['unit_cost'].astype(float) 

        rename_cols_dict = {
            'unit_cost': 'mac', 'ndc':'mac_ndc'
        }
        pbm_hippo_historic_df = pbm_hippo_historic_df.rename(columns = rename_cols_dict)
        pbm_hippo_historic_df = pbm_hippo_historic_df[['mac_ndc', 'mac', 'valid_from', 'valid_to']]

    return pbm_hippo_historic_df.drop_duplicates().reset_index(drop=True)
