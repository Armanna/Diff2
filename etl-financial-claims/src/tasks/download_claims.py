from io import BytesIO

import sources.claims as claims
from transforms import utils
from hippo.exporters import Registry
from hippo.exporters import s3 as s3_exporter
from hippo.sources import claims_downloader
from hippo.sources.claims import FillsAndReversals, BasisOfReimbursment, FillStatus, Partners
from hippo import logger

log = logger.getLogger('download_claims.py')

def run(inter_period_dict, run_date, period, financial_claims_bucket, financial_claims_temp_files_prefix, s3_exporter_enabled, **kwargs):
    print('inter_period_dict >>>', inter_period_dict)
    print('run_date >>>', run_date)
    print('period >>>', period)
    print('financial_claims_bucket >>>', financial_claims_bucket)
    print('financial_claims_temp_files_prefix >>>', financial_claims_temp_files_prefix)
    print('s3_exporter_enabled >>>', s3_exporter_enabled)



    log.info(f"\nRun date is: {run_date}. Inter period flag is {inter_period_dict['status']}")
    log.info(f"period: \n {period}")
    log.info(f"period: \n {financial_claims_bucket}")
    log.info(f"period: \n {financial_claims_temp_files_prefix}")

    if period not in ['day','week', 'month', 'quarter']:
        raise Exception('Report flag must be set to "day", "week", "month" or "quarter". Check the period parameter.')

    # initialize dates for current and previous reports. Change the timedelta or DateOffset in case you want to make reports different from current week or month.
    current_report_date, previous_report_date, current_month_date = utils.process_report_dates(period, run_date, inter_period_flag=inter_period_dict['status'])

    print('#######################################################')
    print('current_report_date >>>', current_report_date)
    print('previous_report_date >>>', previous_report_date)
    print('current_month_date >>>', current_month_date)



    claims_downloader_dates = utils.process_claims_dates(current_report_date, current_month_date, period, inter_period_dict['status'])
    log.info(f"\nDownloading claims for period: {claims_downloader_dates['period_start']} - {claims_downloader_dates['period_end']}")

    # download claims from the DB based on the date of current period not current day
    claims_src = claims_downloader.ClaimsDownloader(period_start = claims_downloader_dates['period_start'], period_end = claims_downloader_dates['period_end'], 
    fills_and_reversals = FillsAndReversals.FILLS_AND_REVESALS, fill_status=FillStatus.FILLED, partners=Partners.ALL, print_sql_flag=True)
    
    claims_df = claims_src.pull_data()
    claims_df = claims.process_claims(claims_df)
    print(claims_df)

    buffer = BytesIO()
    claims_df.to_parquet(buffer, compression='snappy', engine='pyarrow')
    log.info(f"Saving data in {financial_claims_bucket}/{financial_claims_temp_files_prefix}")
    export = Registry()\
            .add_exporter('s3', s3_exporter.S3Exporter(
                financial_claims_bucket,
                financial_claims_temp_files_prefix,
                enabled=s3_exporter_enabled,
            ))

    export.emit('claims.parquet', buffer)
