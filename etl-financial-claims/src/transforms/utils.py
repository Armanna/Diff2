import pandas as pd
import numpy as np
import re
import ast
import datetime as dt
import yaml
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from decimal import * 
from itertools import product
from sources.partners.string_constants import get_partner_group
from transforms import pandas_helper

from hippo.exporters import Registry
from hippo.exporters import s3 as s3_exporter
from hippo.exporters import fs as fs_exporter

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from hippo import logger

log = logger.getLogger('utils.py')

def process_airflow_config_variables(**kwargs):
  run_date = kwargs.pop('run_date', None) 
  inter_period_flag = kwargs.pop('inter_period_flag', None)
  email_exporter_enabled = kwargs.pop('email_exporter_enabled', None) 
  period = kwargs.get('period')
  to_emails = kwargs.pop('to_emails', None) 
  kwargs['run_date'] = parse_current_report_day(run_date)
  kwargs['inter_period_dict'] = parse_inter_period_flag(inter_period_flag, kwargs['run_date'], period)
  email_dict = parse_emails(to_emails, email_exporter_enabled)
  kwargs['to_emails'] = email_dict['to_emails']
  kwargs['email_exporter_enabled'] = email_dict['email_exporter_enabled']
  kwargs['processed_vars'] = [f"Processed env variables are: - run_date: {kwargs['run_date']}; inter_period_flag: {kwargs['inter_period_dict']['status']}; email_exporter_enabled: {kwargs['email_exporter_enabled']}; to_emails: {kwargs['to_emails']}"]
  return kwargs

def parse_inter_period_flag(inter_period_flag, run_date, period):
  """
  This function needed to distinguish if user want to run defautl report for previous period or needed current period data.
  Also set each montly report scheduled to 16th day of each month as inter-moth report by default.
  In case you want to run inter-month report manually you need to triger DAG w/ config and set {'INTER_PERIOD_FLAG': 'True'}
  """
  if period=='month' and run_date.day >= 16 and inter_period_flag == 'None':
    return {'postfix': '_inter-period', 'status': True}
  elif inter_period_flag == 'None' or inter_period_flag == 'False':
    return {'postfix': '', 'status': False}
  elif inter_period_flag == "True":
    return {'postfix': '_inter-period', 'status': True}

def parse_current_report_day(run_date=None):
  """
  This function needed to run report for any period in the past. By default dag will be using previous period.
  In case you want to set date manually you need to triger DAG w/ config and set it like: {"RUN_DATE": "2023-10-13"}
  """
  if not run_date or run_date == 'None':
    run_date = datetime.now().date()
  else:
    run_date = datetime.strptime(run_date, "%Y-%m-%d")
  return run_date

def parse_emails(to_emails, email_exporter_status):
  """
  This function needed to define email recipients and email_exporter_flag. By default email_exporter_flag will be "True" for prod and "False" for dev, while recipients list:
  "vladimir.talashkevich@hellohippo.com,stead@hellohippo.com,andrew.stead@hellohippo.com,alext@hellohippo.com,charles@hellohippo.com".
  In case recipients list manually defined in DAG Config i.e.: {"TO_EMAILS": "vladimir.talashkevich@hellohippo.com"} - email_exporter_flag will be set to "True" regardless of env. 
  """
  default_recipients = "vladimir.talashkevich@hellohippo.com,stead@hellohippo.com,andrew.stead@hellohippo.com,alext@hellohippo.com,charles@hellohippo.com"
  if not to_emails or to_emails == 'None':
    to_emails = default_recipients
  else:
    email_exporter_status = 'True'
  return {'to_emails': to_emails, 'email_exporter_enabled': email_exporter_status}

def process_report_dates(period, report_date, inter_period_flag=False):
  curdate = report_date
  cur_month = curdate.replace(day = 1)
  if period == 'day':
    days_to_append = 1
    current_report_date = (curdate - dt.timedelta(days = days_to_append)).strftime("%Y-%m-%d")
    previous_report_date = (curdate - dt.timedelta(days = 1 + days_to_append)).strftime("%Y-%m-%d")
    current_month = datetime.strptime(current_report_date, "%Y-%m-%d").replace(day = 1).strftime("%Y-%m-%d")
  elif period == 'week':
    days_to_append = 7
    current_report_date = (curdate - dt.timedelta(days = datetime.weekday(curdate) + days_to_append)).strftime("%Y-%m-%d")
    previous_report_date = (curdate - dt.timedelta(days = datetime.weekday(curdate) + 7 + days_to_append)).strftime("%Y-%m-%d")
    current_month = datetime.strptime(current_report_date, "%Y-%m-%d").replace(day = 1).strftime("%Y-%m-%d")
  elif period == 'month' and inter_period_flag==False:
    current_report_date = (cur_month - pd.DateOffset(months=+1)).strftime("%Y-%m-%d")
    previous_report_date = (cur_month - pd.DateOffset(months=+2)).strftime("%Y-%m-%d")
    current_month = cur_month.strftime("%Y-%m-%d")
  elif period == 'month' and inter_period_flag==True:
    current_report_date = curdate.replace(day = 16).strftime("%Y-%m-%d")
    previous_report_date = (cur_month - pd.DateOffset(months=+1)).replace(day = 16).strftime("%Y-%m-%d")
    current_month = cur_month.strftime("%Y-%m-%d")
  elif period == 'quarter':
      cur_quarter = (curdate.month - 1) // 3 + 1
      if cur_quarter == 1: # avoid error when we run the report in 1st quarter of the year and expect Q4 dates from past year
          current_report_date = curdate.replace(year=(curdate.year - 1),month=10, day=1)
      else:
          current_report_date = curdate.replace(month=(cur_quarter - 1) * 3 - 2, day=1)
      
      previous_report_date = (current_report_date - pd.DateOffset(months=3)).replace(day=1).strftime("%Y-%m-%d")
      current_report_date = current_report_date.strftime("%Y-%m-%d")
      current_month = curdate.replace(day=1).strftime("%Y-%m-%d")
  else:
    raise Exception('Time period different to "week" or "month" not supported')
  return current_report_date, previous_report_date, current_month

def process_claims_dates(current_report_date, current_month, period, inter_period_flag=False):
    """
    This fuction calculates period_start and period_end for claims_downloader based on the report period (month or week) and RUN_DATE.
    In both cases we need whole month data both for weekly and monthly reports. The only exception - inter month period.
    For inter-month report we download claims for the period 1st - 16th day of the month. Month for inter-period report could be also manualy set with RUN_DATE DAG parameter. 
    """
    claims_downloader_dates = {}
    if inter_period_flag==True: # if it's iner-month report - download claims for the period 1st - 16th day of the month 
      start_date = current_month
      end_date = current_report_date
      claims_downloader_dates.update({'period_start': start_date, 'period_end': end_date})
    else:
      if period == 'quarter':
        start_date = current_report_date
        claims_downloader_dates.update({'period_start': start_date})
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = start_date + relativedelta(months=3, days=-1)
        end_date = end_date.strftime('%Y-%m-%d')
        claims_downloader_dates.update({'period_end': end_date})
      else:
        start_date = current_report_date if period == 'month' else current_month
        claims_downloader_dates.update({'period_start': start_date})
        current_report_date = datetime.strptime(current_report_date, '%Y-%m-%d')
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        report_week_last_day = current_report_date + relativedelta(days=6)
        end_date = start_date + relativedelta(months=1, days=-1)
        if report_week_last_day > end_date: # in case last day of the report week is next month to first day we need to extend claims downloader dates range
            end_date = report_week_last_day
        end_date = end_date.strftime('%Y-%m-%d')
        claims_downloader_dates.update({'period_end': end_date})
    return claims_downloader_dates

def calculate_previous_month(current_month_date):
  previous_month_date = datetime.strptime(current_month_date, '%Y-%m-%d')
  previous_month_date = previous_month_date + relativedelta(months=-1)
  previous_month_date = previous_month_date.strftime('%Y-%m-%d')
  return previous_month_date

def cast_columns_to_decimal(df, column_names, fillna_flag=False):
  for column in column_names:
    if fillna_flag:
        df[column] = df[column].fillna(Decimal(0)).apply(lambda x: Decimal(x))
    else:
        df[column] = df[column].apply(lambda x: Decimal(x))
  return df

def cast_cents_to_dollars(df, column_names):
  df.update(df.loc[:, column_names].divide(100))
  return df

def rename_columns_for_monthly_report(dict_of_dfs, period_variables):
  for name, df in dict_of_dfs.items():
    cols = df.columns.tolist()
    new_cols = {}
    for col in cols:
      if col.endswith('_period_postfix'):
        new_cols[col] = col.replace('_period_postfix', period_variables['column_postfix'])
      if col.endswith('period_avg_postfix'):
        new_cols[col] = col.replace('_period_avg_postfix', period_variables['avg_col_postfix'])
    df.rename(columns=new_cols, inplace=True)
  return dict_of_dfs

def load_period_variables_financials_claims_preprocess(period):
  with open("./sources/financials_claims.yml", "r") as f:
      data = yaml.safe_load(f)
  dictionary = data[period]
  return dictionary

def add_columns(df, column_names):
    col_num = df.shape[1]
    for column_name in column_names:
        df.insert(loc=col_num, column=column_name, value=np.nan)
        col_num = col_num + 1
    return df

def replace_date_part_of_the_string(original_string):
  """
  this function take any partner financials hystorical file name as an argument {file_name}_{file_date}.csv and transform it to {file_name}_default.csv
  """
  parts = original_string.split("_")
  parts[-1] = 'default'  # Replace date part with 'default'
  modified_string = "_".join(parts)  # Join the parts back into a string
  return modified_string

def group_and_aggregate(df, type: str, groupby_list: list, agg_dict_upd = {}, current_report_date = '', partner = ''):
  if len(groupby_list) > 2 and 'partner' not in groupby_list : ## groupby_list items different from reversal/fills period and partner, special case for WebMD
    aggregation_dict = {
        type: ('rx_id','count'),
        f'new_user_{type}': ('new','sum'),
        f'returning_user_{type}': ('returning','sum'),
        'hippo_net_revenue': ('net_revenue','sum'),
        'net_drug_costs': ('net_drug_costs','sum'),
        'execution_costs': ('erx_cost','sum'), 
        'margin_a': ('margin','sum'),
        'change_margin_a': ('change_margin','sum'),
        'processor_fee': ('processor_fee','sum'),
        'ingredient_cost_upside_usd': ('ingredient_cost_upside_usd', 'sum'),
        'dispensing_fee_upside_usd': ('dispensing_fee_upside_usd', 'sum'),
        'margin_upside_usd': ('margin_upside_usd', 'sum'),
      }
    if type == 'reversals':
      dict_split_reversals = {
        'net_reversals': ('valid_from', lambda x: (x < current_report_date).sum()),
        'within_reversals': ('valid_from', lambda x: (x >= current_report_date).sum()),
      }
      aggregation_dict.update(dict_split_reversals)
    aggregation_dict.update(agg_dict_upd)

    df = df.groupby(groupby_list).agg(**aggregation_dict).assign(partner = partner).reset_index()
  else:
    aggregation_dict = {
        type: ('rx_id','count'),
        f'new_user_{type}': ('new','sum'),
        f'returning_user_{type}': ('returning','sum'),
        'hippo_net_revenue': ('net_revenue','sum'),
        'net_drug_costs': ('net_drug_costs','sum'),
        'execution_costs': ('erx_cost','sum'), 
        'margin_a': ('margin','sum'),
        'change_margin_a': ('change_margin','sum'),
        'processor_fee': ('processor_fee','sum'),
      }
    aggregation_dict.update(agg_dict_upd)
    df = df.groupby(groupby_list, as_index = False).agg(**aggregation_dict).assign(partner = partner).reset_index()

  return df

def update_inter_month_dates(df_column: pd.Series):
  # Replace the last part of the strings in the 'month' column with '16'
  df_column = df_column.str.replace(r'-\d{2}$', '-16', regex=True)
  return df_column

def build_historical_prefix(partner_financials_prefix, previous_week_dates_dict):
  historical_prefixes_dict = {}
  for key, value in previous_week_dates_dict.items():
    historical_prefix = _replace_prefix_date(partner_financials_prefix, key)
    historical_prefixes_dict.update({value: historical_prefix})
  return historical_prefixes_dict

def get_previous_weeks_dates(input_date):
  """
  within weekly report we need to add historical hippo_margin data per partner for 90/180/360 days before current week
  this data will be automatically downloaded from respective s3 prefix if it's available
  this function calculates dates of weeks that have been 90/180/360 days before current week
  """
  input_date = datetime.strptime(input_date, '%Y-%m-%d')
  week_gaps = [13, 26, 52]  # List of week
  previous_week_dates_dict = {}
  for weeks in week_gaps:
    previous_report_date = input_date - timedelta(weeks=weeks)
    previous_prefix_date = input_date - timedelta(weeks=weeks-1)
    formatted_date = previous_report_date.strftime('%Y-%m-%d')
    formatted_prefix_date = previous_prefix_date.strftime('%Y-%m-%d')
    previous_week_dates_dict[formatted_prefix_date] = formatted_date
  return previous_week_dates_dict

def _replace_prefix_date(prefix, date):
  replacement_string = date.replace('-', '.')
  date_pattern = r'\d{4}\.\d{2}\.\d{2}'
  prefix = re.sub(date_pattern, replacement_string, prefix)
  return prefix

def _generate_template(aggregate_fills_df, partner):
    partner_group = get_partner_group(partner)

    dict_dimension_template = {
        'contract_name': aggregate_fills_df['contract_name'].unique().tolist(),
        'program_name': aggregate_fills_df['program_name'].unique().tolist(),
        'sub_program_name': aggregate_fills_df['sub_program_name'].unique().tolist(),
        'reconciliation_program': aggregate_fills_df['reconciliation_program'].unique().tolist(),
        'reconciliation_program_annotation': aggregate_fills_df['reconciliation_program_annotation'].unique().tolist(),
        'partner'            : [partner], ## partner name
        'partner_group'            : [partner_group],
        'new_returning_flag' : ['new', 'returning'],                                ## new and returning
        'fill_reversal_flag' : ['fills', 'reversals'],                              ## fill and reversal
        'brand_generic_flag' : ['brand', 'generic'],                                ## brand and generic
        'chain_name'         : aggregate_fills_df['chain_name'].unique().tolist()   ## list of all the chains
    }
    
    template_df = pd.DataFrame(list(product(
      dict_dimension_template['contract_name'], 
      dict_dimension_template['program_name'], 
      dict_dimension_template['sub_program_name'],
      dict_dimension_template['reconciliation_program'], 
      dict_dimension_template['reconciliation_program_annotation'], 
      dict_dimension_template['partner'],
      dict_dimension_template['partner_group'], 
      dict_dimension_template['new_returning_flag'], 
      dict_dimension_template['fill_reversal_flag'], 
      dict_dimension_template['brand_generic_flag'], 
      dict_dimension_template['chain_name'])
    ), columns = dict_dimension_template.keys())

    return template_df

def process_partner_alerts(
    partner_raw_dfs, partner, period, slack_channel, slack_bot_token,
    header_printed, report_date, financial_claims_bucket, s3_exporter_enabled
):
    date = report_date.replace("-", ".")
    download_command = (
        f"Download command:\n"
        "```\n"
        f"aws s3 cp s3://{financial_claims_bucket}/alerts/{period}/{date}/ /tmp/alerts/{period}/{date}/ --recursive\n"
        "```\n"
    )        
    result_dict = validate_key_columns_integrity(
        partner_raw_dfs[partner], 
        ['partner','chain_name','partner_group', 'contract_name', 'brand_generic_flag', 'new_returning_flag'], 
        partner, 
        period, 
        slack_channel, 
        slack_bot_token,
        download_command,
        header_printed  # passing a list to track the header printing across iterations
    )
    
    for name, df in result_dict.items():
        export = Registry()\
            .add_exporter('fs', fs_exporter.FSExporter("/tmp")) \
            .add_exporter('s3', s3_exporter.S3Exporter(
                financial_claims_bucket,
                f"alerts/{period}/{date}/",
                enabled=s3_exporter_enabled,
            ))
        export.emit(name, df)

def validate_key_columns_integrity(df: pd.DataFrame, columns_to_check: list, partner, period, slack_channel, slack_bot_token, text, header_printed: list) -> dict:
  null_dict = {}
  msg_header = f":rotating_light::rotating_light: Financial claims data require attention. Period: {period} :rotating_light::rotating_light:\n" + text

  for col in columns_to_check:
      null_count = df[col].isnull().sum()
      # If the column contains null values
      if null_count > 0:
          key = f"{partner}_{col}"
          msg = f"Partner: {partner}. Column '{col}' has {null_count} null values."
          if not header_printed[0]:
            msg = msg_header + msg
            header_printed[0] = True
          send_text_message_to_slack(slack_channel, slack_bot_token, msg)
          null_dict[key] = df[df[col].isnull()]

  return null_dict

def send_text_message_to_slack(slack_channel, slack_bot_token, text_msg):
  # send text message to the specific slack channel
  client = WebClient(token=slack_bot_token)

  try:
      result = client.chat_postMessage(
          channel=slack_channel,
          text=text_msg
      )
      # Log the result
      log.info(result)

  except SlackApiError as e:
      log.info(f"Error sending message to Slack: {e.response['error']}")

def add_mac_data(partner_df, mac_cost_v2_history_dfs):
  """
  this function joins MAC unit_cost based on the chain_code
  """
  filtered_dfs_list = []
  dfs_plus_mac_list = []
  
  # filter partners dataframes based on chain_codes
  all_chain_codes_list = []
  for key, mac_df in mac_cost_v2_history_dfs.items():
      chain_codes = eval(key)  # converts string representation of a list to an actual list
      all_chain_codes_list.extend(chain_codes) # save MAC chain codes into one list
      
      # filter partners dataframes
      filtered_df = partner_df[partner_df['chain_code'].isin(chain_codes)]
      if not filtered_df.empty:
          filtered_dfs_list.append((filtered_df, mac_df))
  
  # identify rows in partner_df not matching any chain_codes
  not_a_mac_df = partner_df[~partner_df['chain_code'].isin(all_chain_codes_list)]
  
  # perform left joins for each filtered DataFrame and add the MAC data
  for filtered_df, mac_df in filtered_dfs_list:
      if not filtered_df.empty:
          data = pandas_helper.left_join_with_condition_preserve_index(
        filtered_df,
        mac_df,
        left_on='product_id',
        right_on='ndc'
    ).drop(columns={'ndc'})
          dfs_plus_mac_list.append(data)

  not_a_mac_df['mac'] = np.nan

  # combine all DataFrames
  result_df = pd.concat(dfs_plus_mac_list + [not_a_mac_df], ignore_index=True)

  return result_df

def convert_to_list(value):
  # conver dataframe column from string to list
  if isinstance(value, str) and value.startswith('[') and value.endswith(']'):
      return ast.literal_eval(value)
  return [value]
