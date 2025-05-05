from io import BytesIO
from transforms import utils
import pandas as pd
import sources.rank as rank
import sources.r_claim_proc_fees as claims_processing_fees
import sources.partners.good_rx.hd_goodrx_feed_mac_prices_history as goodrx_mac
import sources.partners.all_partners as all_partners
from hippo.exporters import Registry
from hippo.exporters import s3 as s3_exporter
from hippo.sources.download_sources import SourceDownloader, HistoricalData, HistoricalDataPbmHippo
from hippo import logger

import datetime

log = logger.getLogger('download_other_sources.py')

def run(inter_period_dict, run_date, period, financial_claims_bucket, financial_claims_temp_files_prefix, s3_exporter_enabled, **kwargs):
    log.info(f"\nRun date is: {run_date}. Inter period flag is {inter_period_dict['status']}")
    log.info(f"period: \n {period}")
    log.info(f"Financial claims bucket: \n {financial_claims_bucket}")
    log.info(f"Financial claims temp prefix: \n {financial_claims_temp_files_prefix}")

    if period not in ['day','week', 'month', 'quarter']:
        raise Exception('Report flag must be set to "day", "week", "month" or "quarter". Check the period parameter.')

    # initialize dates for current and previous reports. Change the timedelta or DateOffset in case you want to make reports different from current day, week or month.
    current_report_date, previous_report_date, current_month_date = utils.process_report_dates(period, run_date, inter_period_flag=inter_period_dict['status'])

    print('current_report_date >>>', current_report_date)
    print('previous_report_date >>>', previous_report_date)
    print('current_month_date >>>', current_month_date)

    claims_downloader_dates = utils.process_claims_dates(current_report_date, current_month_date, period, inter_period_dict['status'])
    log.info(f"\nDownloading claims for period: {claims_downloader_dates['period_start']} - {claims_downloader_dates['period_end']}")

    print('claims_downloader_dates >>>', claims_downloader_dates)

    # download claims from the DB based on the date of current period not current day
    src = SourceDownloader(tables=[HistoricalData.GOODRX_NPI_RS, HistoricalData.NDC_COST_V2_S3, HistoricalData.NDC_V2_S3, HistoricalData.PHARMACY_S3], get_modified_dfs=True) 
    source_dict = src.generate_sources_dictionary()

    print('len source_dict >>>', len(source_dict), source_dict.keys())

    ## Getting list of all partners fees
    all_partners_src = all_partners.AllPartners()
    source_dict['all_partners'] = all_partners_src.downloader.pull_partners(sql_text=all_partners_src.partner_financials_sql)

    ## Getting ranks to define if a user is new or returning
    rank_src = rank.RankSource(claims_downloader_dates['period_start'], claims_downloader_dates['period_end'], period)
    source_dict['rank'] = rank_src.downloader.pull_rank(sql_text=rank_src.partner_financials_sql)

    ## Getting processing fees
    claims_processing_fees_src = claims_processing_fees.ClaimsProcFeesSource(claims_downloader_dates['period_start'], claims_downloader_dates['period_end'])
    source_dict['claim_processing_fees'] = claims_processing_fees_src.downloader.pull_claim_processing_fees(sql_text=claims_processing_fees_src.partner_financials_sql)
    
    ## Getting mac list
    goodrx_mac_src = goodrx_mac.GoodrxFeedMacSource(claims_downloader_dates['period_start'], claims_downloader_dates['period_end'])
    source_dict['goodrx_feed_mac'] = goodrx_mac_src.downloader.pull_goodrx_feed_mac_prices(sql_text=goodrx_mac_src.partner_financials_sql)

    source_dict = filter_dataframes(source_dict)

    print('Final source_dict keys >>>', source_dict.keys())

    for name, df in source_dict.items():
        if 'valid_to' in df.columns.tolist():
            # store data as of 3rd of Jan 2024 as Walmart requires it
            # or store data for last 300 days whatever is earlier
            final_date_threshold = pd.to_datetime(claims_downloader_dates['period_start'],format='%Y-%m-%d') - pd.Timedelta(days=300)
            if name == 'ndc_costs_v2' or name == 'ndcs_v2':
                january_2nd_2024 = datetime.datetime(2024, 1, 2)
                final_date_threshold = min(final_date_threshold, january_2nd_2024)

            df = df[df['valid_to'] > final_date_threshold]

        if 'valid_from' in df.columns.tolist():
            df = df[df['valid_from'] < pd.to_datetime(claims_downloader_dates['period_end'],format='%Y-%m-%d') + pd.Timedelta(days=1)]

        buffer = BytesIO()
        df.to_parquet(buffer, compression='snappy', engine='pyarrow')
        log.info(f"Saving {name} data in {financial_claims_bucket}/{financial_claims_temp_files_prefix}")
        export = Registry()\
                .add_exporter('s3', s3_exporter.S3Exporter(
                    financial_claims_bucket,
                    financial_claims_temp_files_prefix,
                    enabled=s3_exporter_enabled,
                ))

        export.emit(f'{name}.parquet', buffer)

def filter_dataframes(dict):
    for key, df in dict.items():
        if key == 'goodrx_feed_npi_groups_history':
            df = df[['npi','valid_from','valid_to','price_group']]
            df['npi'] = df['npi'].astype('int64')
        elif key == 'ndc_costs_v2':
            df = df[['ndc','nadac','gpi_nadac','wac','awp','valid_from','valid_to']]
            df['ndc'] = df['ndc'].astype(str).str.zfill(11)
            df[['nadac','gpi_nadac','awp','wac']] = df[['nadac','gpi_nadac','awp','wac']].astype(float)
        elif key == 'ndcs_v2':
            df = df[['id','is_otc','valid_from','valid_to','nadac_is_generic', 'multi_source_code', 'name_type_code']]
            df['id'] = df['id'].astype(str).str.zfill(11)
            df['is_otc'] = df['is_otc'].convert_dtypes().map({'True': True, 'False': False})
        elif key == 'pharmacy':
            df = df[['id','chain_name','chain_code','valid_from','valid_to','is_in_network', 'state_abbreviation']]
        dict[key] = df
    return dict
        
