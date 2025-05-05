import pandas as pd
from datetime import datetime
from transforms import utils
from hippo.sources.s3 import S3Downloader
from hippo import logger
from hippo import s3

log = logger.getLogger('s3_downloader')


class PartnerFinancialsS3Downloader(S3Downloader):

    def pull_numeric(self, file_suffix='.csv', cents_to_dollars_columns=None, **options):
        s3url = f's3://{self.bucket}/{self.prefix.strip("/")}/{self.name}{file_suffix}'
        log.info('Loading dataframe from {}'.format(s3url))
        df = pd.read_csv(s3url, **options)
        if cents_to_dollars_columns:
            for column in cents_to_dollars_columns:
                df[column] = df[column] / 100
                df[column] = df[column].fillna(0)
        return df

def download_last_period(partner_financials_bucket, partner_financials_last_period_prefix, file_name, run_date, period):
    """
    this method helps to avoid FileNotFoundError while processing period in the past that have no previuos period data to compare with
    in this case default previous report file will be downloaded
    this rule doesn't work for default runs - in case 'run_date > 2023-03-13' for weekly or '> 2023-10-01' for monthly reports - FileNotFoundError will be shown up
    """
    if s3.exists(partner_financials_bucket, f"{partner_financials_last_period_prefix}{file_name}.csv"):
        df = PartnerFinancialsS3Downloader(partner_financials_bucket, partner_financials_last_period_prefix, file_name).pull()[0]
    else:
        if (period == 'week' and run_date < datetime.strptime('2023-03-13', "%Y-%m-%d")) or (period == 'month' and run_date < datetime.strptime('2023-10-01', "%Y-%m-%d")):
            default_file_name = utils.replace_date_part_of_the_string(file_name)
            log.info(f"Previous period file {file_name} wasn't found here {partner_financials_last_period_prefix}{file_name}.csv and will be replaced with default {default_file_name}.")
            df = PartnerFinancialsS3Downloader(partner_financials_bucket, partner_financials_last_period_prefix, default_file_name).pull()[0]
        else:
            log.info(f"FileNotFoundError: Previous period file {file_name} wasn't found")
    return df

def process_summary_financials_history(summary_financials_df, period):
    summary_financials_df = summary_financials_df[summary_financials_df[period] != '2050-01-01']
    summary_financials_df[period] = summary_financials_df[period].astype('datetime64[ns]')
    return summary_financials_df

def process_month_to_date_history(month_to_date_df):
    month_to_date_df = month_to_date_df[month_to_date_df['month'] != '2050-01-01']
    month_to_date_df['month'] = month_to_date_df['month'].astype('datetime64[ns]')
    return month_to_date_df

def download_previous_period_history_weekly(partner_financials_bucket, partner_financials_prefix, partner_financials_last_period_prefix, file_name):
    if s3.exists(partner_financials_bucket, f"{partner_financials_prefix}/{file_name}.csv"):
        df = PartnerFinancialsS3Downloader(partner_financials_bucket, partner_financials_prefix, file_name).pull()[0]
    else:
        default_file_name = utils.replace_date_part_of_the_string(file_name)
        log.info(f"Previous period file {file_name}.csv wasn't found here f'{partner_financials_prefix}/{file_name}.csv' and will be replaced with default {default_file_name}.")
        df = PartnerFinancialsS3Downloader(partner_financials_bucket, partner_financials_last_period_prefix, default_file_name).pull()[0]
    return df
