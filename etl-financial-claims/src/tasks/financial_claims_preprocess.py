import pandas as pd
import datetime
from decimal import Decimal

import sources.utils as sources_utils
import sources.rank as rank
import sources.claims as claims

import sources.s3 as s3
import sources.partners.string_constants as string_constants
import transforms.transform_partner_financials as transform
from transforms.partners.good_rx import good_rx
from transforms.partners.web_md import web_md
from transforms.partners.other_partners import other_partners
from transforms import utils as transforms_utils
from transforms import pandas_helper
from hippo.exporters import Registry
from hippo.exporters import s3 as s3_exporter
from hippo.exporters import fs as fs_exporter
from hippo.exporters import redshift as redshift_exporter
from hippo.sources.s3 import upsert_state
from hippo import logger
from memory_profiler import profile

from sources.chains.contract_program_mapping import SOURCE_DICT_CURRENT_CONTRACTS
 
log = logger.getLogger('financials_claims_preprocess.py')
 
@profile
def run(inter_period_dict, run_date, period, financial_claims_bucket, s3_exporter_enabled, redshift_exporter_enabled, financial_claims_prefix, financial_claims_temp_files_prefix, pbm_hippo_bucket, pbm_hippo_export_prefix, slack_channel, slack_bot_token, **kwargs):

    print('inter_period_dict >>>', inter_period_dict)
    print('run_date >>>', run_date)
    print('period >>>', period)
    print('financial_claims_bucket >>>', financial_claims_bucket)
    print('s3_exporter_enabled >>>', s3_exporter_enabled)
    print('redshift_exporter_enabled >>>', redshift_exporter_enabled)
    print('financial_claims_prefix >>>', financial_claims_prefix)
    print('financial_claims_temp_files_prefix >>>', financial_claims_temp_files_prefix)
    print('pbm_hippo_bucket >>>', pbm_hippo_bucket)
    print('pbm_hippo_export_prefix >>>', pbm_hippo_export_prefix)
    print('slack_channel >>>', slack_channel)
    print('slack_bot_token >>>', slack_bot_token)

    # the list how fills and reversals and merged within the same program
    dimensions_list = ['chain_name', 'contract_name', 'program_name', 'sub_program_name', 'reconciliation_program', 'reconciliation_program_annotation', 'brand_generic_flag', 'fill_reversal_flag', 'new_returning_flag']

    if period not in ['day','week', 'month', 'quarter']:
        raise Exception('Report flag must be set to "day", "week", "month" or "quarter". Check the period parameter.')
 
    # initialize dates for current and previous reports, also helps to name resulting dataframes appropriately. Change the timedelta or DateOffset in case you want to make reports different from current week or month.
      
    print('inter_period_dict >>>', inter_period_dict)
    
    
    current_report_date, previous_report_date, current_month_date = transforms_utils.process_report_dates(period, report_date=run_date, inter_period_flag=inter_period_dict['status'])
    claims_downloader_dates = transforms_utils.process_claims_dates(current_report_date, current_month_date, period, inter_period_dict['status'])

    print('current_report_date >>>', current_report_date)
    print('previous_report_date >>>', previous_report_date)
    print('current_month_date >>>', current_month_date)


    
    
    log.info(f"Running {period}ly report")
    log.info(f"Date range for source files: {claims_downloader_dates['period_start']} - {claims_downloader_dates['period_end']}")
    log.info(f"Report dates: building report for {current_report_date}; Previous report date is: {previous_report_date}.")
    is_s3 = True # False - mean you read data from local storage; True - mean you download from specific s3 bucket/prefix (by default prefix is /temp)
    if is_s3:
        claims_df = s3.PartnerFinancialsS3Downloader(financial_claims_bucket, financial_claims_temp_files_prefix, 'claims.parquet').pull_parquet()[0]
        # claims_df = claims_df.sample(n = 100000, random_state = 1) 
        rank_df = s3.PartnerFinancialsS3Downloader(financial_claims_bucket, financial_claims_temp_files_prefix, 'rank.parquet').pull_parquet()[0]
        claims_processing_fees_df = s3.PartnerFinancialsS3Downloader(financial_claims_bucket, financial_claims_temp_files_prefix, 'claim_processing_fees.parquet').pull_parquet()[0]
        goodrx_mac_df = s3.PartnerFinancialsS3Downloader(financial_claims_bucket, financial_claims_temp_files_prefix, 'goodrx_feed_mac.parquet').pull_parquet()[0]
        goodrx_npi_df = s3.PartnerFinancialsS3Downloader(financial_claims_bucket, financial_claims_temp_files_prefix, 'goodrx_feed_npi_groups_history.parquet').pull_parquet()[0]
        ndcs_cost_v2_history_df = s3.PartnerFinancialsS3Downloader(financial_claims_bucket, financial_claims_temp_files_prefix, 'ndc_costs_v2.parquet').pull_parquet()[0]
        ndcs_v2_history_df = s3.PartnerFinancialsS3Downloader(financial_claims_bucket, financial_claims_temp_files_prefix, 'ndcs_v2.parquet').pull_parquet()[0]
        pharmacy_history_df = s3.PartnerFinancialsS3Downloader(financial_claims_bucket, financial_claims_temp_files_prefix, 'pharmacy.parquet').pull_parquet()[0]
        unique_partners_df = s3.PartnerFinancialsS3Downloader(financial_claims_bucket, financial_claims_temp_files_prefix, 'all_partners.parquet').pull_parquet()[0]
    else:
        claims_df = pd.read_parquet('/tmp/august_daily/claims.parquet')
        # claims_df = claims_df.sample(n = 100000) # uncomment for faster test run during testing 
        rank_df = pd.read_parquet('/tmp/august_daily/rank.parquet')
        claims_processing_fees_df = pd.read_parquet('/tmp/august_daily/claim_processing_fees.parquet')
        goodrx_mac_df = pd.read_parquet('/tmp/august_daily/goodrx_feed_mac.parquet')
        goodrx_npi_df = pd.read_parquet('/tmp/august_daily/goodrx_feed_npi_groups_history.parquet')
        ndcs_cost_v2_history_df = pd.read_parquet('/tmp/august_daily/ndc_costs_v2.parquet')
        ndcs_v2_history_df = pd.read_parquet('/tmp/august_daily/ndcs_v2.parquet')
        pharmacy_history_df = pd.read_parquet('/tmp/august_daily/pharmacy.parquet')
        unique_partners_df = pd.read_parquet('/tmp/august_daily/all_partners.parquet')

    claims_df['product_id'] = claims_df['product_id'].astype(str).str.zfill(11)
    goodrx_mac_df['ndc11'] = goodrx_mac_df['ndc11'].astype(str).str.zfill(11)
    claims_df['quantity_dispensed'] = claims_df['quantity_dispensed'].fillna(0).astype('float64')
    ndcs_v2_history_df['is_otc'] = ndcs_v2_history_df['is_otc'].astype(bool)
 
    ## Getting dictionary with contract/program conditions dataframe
    dict_conditions_per_contract_program = sources_utils.pull_exported_hippo_pbm_file(current_report_date, pbm_hippo_bucket, pbm_hippo_export_prefix,'contract_claims_conditions', dict_current_etl_pbm_hippo_contracts = SOURCE_DICT_CURRENT_CONTRACTS)
    ## Getting dictionary with brand/generic definition per ndc per contract/program
    dict_ndcs_per_contract_program = sources_utils.pull_exported_hippo_pbm_file(current_report_date, pbm_hippo_bucket, pbm_hippo_export_prefix,'ndcs', dict_current_etl_pbm_hippo_contracts = SOURCE_DICT_CURRENT_CONTRACTS)
    ## Getting dictionary with excluded ndcs per contract/program
    dict_mac_per_contract_program = sources_utils.pull_exported_hippo_pbm_file(current_report_date, pbm_hippo_bucket, pbm_hippo_export_prefix,'mac', dict_current_etl_pbm_hippo_contracts = SOURCE_DICT_CURRENT_CONTRACTS)
    # set up parameters for contracts that are using MAC

    # FIXME: Change Healthcare conditions do not exist
    # We need to pull them from etl-pbm-change-healthcare
    # But I will hack for now
    dict_conditions_per_contract_program['change_healthcare'] = {}
    dict_ndcs_per_contract_program['change_healthcare'] = {}

    for program in ['regular', 'unc']:
        ch_df = pd.DataFrame({
            'bin_number': '019876',
            'chain_codes': str([ #FIXME: needs to be cast to str as eval is exexcuted downstream
                '003','025','043','044','069','071','097','108','109',
                '110','113','156','158','171','199','227','232','248','256','273','282',
                '289','292','301','319','400','410','453','463','495','817','832',
                '929','978'
            ]),
            'ingredient_cost_upside_allowed': 'False',
            'dispensing_fee_upside_allowed': 'False',
            'average_admin_fee_allowed': 'False'
        }, index=[0])
        dict_conditions_per_contract_program['change_healthcare'][program] = {}
        dict_conditions_per_contract_program['change_healthcare'][program] = ch_df
        dict_conditions_per_contract_program['change_healthcare'][program]['bin_number'] = dict_conditions_per_contract_program['change_healthcare'][program]['bin_number'].apply(transforms_utils.convert_to_list)

        dict_ndcs_per_contract_program['change_healthcare'][program] = {}
        dict_ndcs_per_contract_program['change_healthcare'][program] = dict_ndcs_per_contract_program['walgreens']['regular'] # all ndcs
        

    # FIXME: Change Healthcare out of network conditions do not exist
    # We need to pull them from etl-pbm-change-healthcare
    # But I will hack for now
    dict_conditions_per_contract_program['out_of_network'] = {}
    dict_ndcs_per_contract_program['out_of_network'] = {}

    for program in ['regular', 'unc']:
        ch_df = pd.DataFrame({
            'bin_number': '019876',
            'chain_codes': str([ #FIXME: replace placeholder with all rest chain_codes
                None, 
            ]),
            'ingredient_cost_upside_allowed': 'False',
            'dispensing_fee_upside_allowed': 'False',
            'average_admin_fee_allowed': 'False'
        }, index=[0])
        dict_conditions_per_contract_program['out_of_network'][program] = {}
        dict_conditions_per_contract_program['out_of_network'][program] = ch_df
        dict_conditions_per_contract_program['out_of_network'][program]['bin_number'] = dict_conditions_per_contract_program['out_of_network'][program]['bin_number'].apply(transforms_utils.convert_to_list)

        dict_ndcs_per_contract_program['out_of_network'][program] = {}
        dict_ndcs_per_contract_program['out_of_network'][program] = dict_ndcs_per_contract_program['walgreens']['regular'] # all ndcs
        

    to_export_common_block = {}

    ## Setting up dictionaries to collect data
    partner_raw_dfs = {}
    partner_aggregated_dfs = {}

    ## Getting relevant dates based on period, e.g. day, week or month
    report_date, previous_start_date, current_month_date = transforms_utils.process_report_dates(period, report_date=run_date, inter_period_flag=inter_period_dict['status'])

    ## Filtering and join data to claims
    current_report_raw_data_df = transform.process_current_period_data_per_chain(claims_df, rank_df, period, report_date, previous_start_date)

    # create raw partners dataframes:
    per_claim_fills_df = transform.process_raw_claims(current_report_raw_data_df, claims_processing_fees_df, rank_df, pharmacy_history_df, period, unique_partners_df)

    header_printed = [False] # need this flag to track alerts printed to slack

    for partner in unique_partners_df['partner']:
        log.info("processing partner: %s", partner) 

        if partner not in per_claim_fills_df['partner'].unique().tolist():
            indexes_to_drop = unique_partners_df[unique_partners_df['partner'] == partner].index
            unique_partners_df = unique_partners_df.drop(indexes_to_drop)
            log.info(f"{partner} deleted from unique_partners_df")
            continue

        partner_raw_dfs[partner] = transform.process_raw_partner_dataframes(per_claim_fills_df, partner, current_report_date, period)
        log.info(f'Filtered {partner} partner claims only')

        if partner_raw_dfs[partner].empty:
            indexes_to_drop = unique_partners_df[unique_partners_df['partner'] == partner].index
            unique_partners_df = unique_partners_df.drop(indexes_to_drop)
            log.info(f"{partner} deleted from unique_partners_df, skipping to the next partner")
            continue

        ## replace claim_date_of_service for Walmart NADAC claims with new contract
        original_claim_date_of_service = partner_raw_dfs[partner]['claim_date_of_service'].copy()

        sep_3rd_2024 = pd.Timestamp(datetime.datetime(2024, 9, 3))
        jan_3rd_2024 = pd.Timestamp(year=2024, month=1, day=3, hour=12) # need to make it 12pm similar to other claim_date_of_service
        walmart_condition = (partner_raw_dfs[partner]['chain_name'] == 'walmart') & (partner_raw_dfs[partner]['claim_date_of_service'] >= sep_3rd_2024) & (partner_raw_dfs[partner]['basis_of_reimbursement_determination_resp'] == '20')
        partner_raw_dfs[partner].loc[walmart_condition, 'claim_date_of_service'] = jan_3rd_2024

        partner_raw_dfs[partner] = pandas_helper.left_join_with_condition_preserve_index(partner_raw_dfs[partner], ndcs_v2_history_df, left_on='product_id', right_on='id')
        log.info("Added ndcs history")
        partner_raw_dfs[partner] = pandas_helper.left_join_with_condition_preserve_index(partner_raw_dfs[partner], ndcs_cost_v2_history_df, left_on='product_id', right_on='ndc').drop(columns={'ndc'})
        log.info("Added ndc costs history")
        partner_raw_dfs[partner]['is_otc'] = partner_raw_dfs[partner]['is_otc'].astype(bool)


        # after adding NDCs and NDC costs return back original claim_date_of_service data
        partner_raw_dfs[partner]['claim_date_of_service'] = original_claim_date_of_service

        partner_raw_dfs[partner] = partner_raw_dfs[partner].reset_index(drop = True)

        partner_raw_dfs[partner]['mac'] = transform.join_mac_cost(
            partner_raw_dfs[partner][[
                'user',
                'chain_name',
                'chain_code',
                'claim_date_of_service',
                'valid_from',
                'valid_to',
                'partner',
                'partner_group',
                'bin_number',
                'network_reimbursement_id',
                'product_id'
            ]],
            partner, 
            SOURCE_DICT_CURRENT_CONTRACTS, 
            dict_conditions_per_contract_program, 
            dict_ndcs_per_contract_program,
            dict_mac_per_contract_program
        )
        log.info("Added MAC data")

        partner_raw_dfs[partner][['partner_group', 'contract_name', 'program_name', 'sub_program_name', 'reconciliation_program', 'reconciliation_program_annotation', 'brand_generic_flag', 'ingredient_cost_upside_usd', 'dispensing_fee_upside_usd', 'margin_upside_usd']] = transform.calculate_contracted_elements(
            partner_raw_dfs[partner][[
                'ingredient_cost_paid_resp',
                'dispensing_fee_paid_resp',
                'total_paid_response',
                'quantity_dispensed',
                'awp',
                'wac',
                'mac',
                'chain_name',
                'is_otc',
                'days_supply',
                'claim_date_of_service',
                'valid_from',
                'valid_to',
                'gpi_nadac',
                'nadac',
                'state_abbreviation',
                'partner',
                'partner_group',
                'bin_number',
                'network_reimbursement_id',
                'chain_code',
                'product_id',
                'dispense_as_written',
                'basis_of_reimbursement_determination_resp',
                'usual_and_customary_charge',
                'user',
                'npi',
                'rx_id',
                'cardholder_id',
                'n_cardholder_id',
                'multi_source_code',
                'nadac_is_generic',
                'name_type_code',
            ]], 
            current_report_date, 
            SOURCE_DICT_CURRENT_CONTRACTS, 
            dict_conditions_per_contract_program, 
            dict_ndcs_per_contract_program
        )

        transforms_utils.process_partner_alerts(partner_raw_dfs, partner, period, slack_channel, slack_bot_token, header_printed, report_date, financial_claims_bucket, s3_exporter_enabled)

    if 'webmd' in unique_partners_df['partner'].values:
        log.info("Aggregating partner: %s", 'webmd')
        partner_aggregated_dfs['webmd'] = web_md.process_webmd_claims_per_chain(partner_raw_dfs['webmd'], report_date, period, dimensions_list, partner='webmd')

    log.info("Aggregating partner: %s", 'GoodRx')
    partner_aggregated_dfs['GoodRx'] = good_rx.process_goodrx_claims_per_chain(claims_processing_fees_df, claims_df, partner_raw_dfs['GoodRx'], goodrx_npi_df, goodrx_mac_df, period, report_date, dimensions_list, partner='GoodRx', **kwargs)

    # create clean dataframes for "rest partners": Other, Direct, TPDT, save.health, WebMD and Famulus
    for partner in unique_partners_df['partner']:
        if partner in (['GoodRx', 'webmd']):
            continue
        log.info("Aggregating partner: %s", partner)
        partner_aggregated_dfs[partner] = other_partners.process_rest_partners_claims_per_chain(partner_raw_dfs[partner], period, report_date, dimensions_list, partner)


    ## Concatenated all partner dataframes in a single one
    all_partners_df = pd.DataFrame()
    for partner in unique_partners_df['partner']:
        log.info("merging partner: %s", partner)
        log.info("partner df shape: %s", partner_aggregated_dfs[partner].shape)

        if partner_aggregated_dfs[partner].empty:
            log.info("%s partner has 0 rows. Skipping", partner)
            continue

        # Make sure data is clean and tidy before merging
        # As there is a lot of custom code which needs to be group into single
        # For now the only efficient way to process is to process as is and then cleanup.
        # FIXME: But eventually this code should be definitely moved out of main method
        partner_df = partner_aggregated_dfs[partner].copy()
        partner_df = partner_df[~pd.isnull(partner_df['fills'])]
        partner_df['fills'] = partner_df['fills'].astype(int)
        partner_df['reversals'] = partner_df['reversals'].astype(int)
        partner_df = partner_df[(partner_df['fills'] > 0) | (partner_df['reversals'] > 0)].reset_index(drop=True)

        all_partners_df = pd.concat([all_partners_df, partner_df], ignore_index=True).reset_index(drop=True)

    all_partners_df[period] = current_report_date
    all_partners_df[period] = all_partners_df[period].astype('datetime64[ns]')
    
    ## sometimes the order is messed up. Below is the attempt to fix the order so Redshift upload happens correctly.
    desired_order = [
        'partner', 'partner_group', 'fills', 'net_fills', 'new_user_fills', 'refills', 
        'returning_user_fills', 'reversals', 'net_revenue', 'net_drug_costs', 
        'transaction_costs', 'erx_execution_costs', 'change_margin', 'hippo_margin', 
        'partner_margin', 'net_margin', 'margin_per_fill', 'hippo_margin_per_fill', 
        'ingredient_cost_upside_usd', 'dispensing_fee_upside_usd', 'margin_upside_usd', 
        'net_reversals', 'within_reversals', 'chain_name', 'contract_name', 
        'program_name', 'sub_program_name', 'reconciliation_program', 
        'reconciliation_program_annotation', 'brand_generic_flag', 'fill_reversal_flag', 
        'new_returning_flag', period
    ]

    all_partners_df = all_partners_df[desired_order]

    log.info("All partner df shape: %s", all_partners_df.shape)
    
    ## Creating dictionary to save each dataframe to be exported
    report_date_styled = report_date.replace('-', '.')
    to_export_common_block[f'agg_data_by_{period}'] = {'df': all_partners_df,
                                                                            'period': period,
                                                                            'report_date': report_date_styled}

    
    print('----------', f"{financial_claims_prefix}{period}/{report_date_styled}/")
    
    for name, dict_period_df in to_export_common_block.items():
        period = dict_period_df['period']
        df = dict_period_df['df']
        report_date = dict_period_df['report_date']
        export = Registry()\
        .add_exporter('fs', fs_exporter.FSExporter("/tmp")) \
        .add_exporter('s3', s3_exporter.S3Exporter(
            financial_claims_bucket,
            f"{financial_claims_prefix}{period}/{report_date_styled}/",
            enabled=s3_exporter_enabled,
        ))\
        # .add_exporter('redshift', redshift_exporter.RedshiftExporter(                        ## This will be commented until the validation process finish, to avoid inserting multiple testing records into redshift
        #     financial_claims_bucket, f"{financial_claims_prefix}{period}/{report_date_styled}/", 
        #     schema="financial_claims", enabled=redshift_exporter_enabled,
        #     append=True, drop_duplicates=True, drop_duplicates_on=[period], drop_duplicates_keep_strategy='last'
        # ))
        export.emit(name, df)
