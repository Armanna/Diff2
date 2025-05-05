import os
from datetime import datetime, timedelta
from airflow import DAG
from lib.operators.glue import HippoGlueJobOperator
from lib.v2 import utils

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2022, 12, 19, 9, 00, 00),
    'email': ['diego@hellohippo.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'on_failure_callback': utils.send_slack_message,
    'on_retry_callback': utils.send_slack_message,
    'retry_delay': timedelta(minutes=30),
}

AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID")
AWS_REGION = os.getenv("AWS_REGION")

FINANCIAL_CLAIMS_BUCKET = 'etl-financial-claims-{}-{}'.format(AWS_ACCOUNT_ID, AWS_REGION)
PHARMACY_HISTORY_BUCKET = 'etl-pharmacy-{}-{}'.format(AWS_ACCOUNT_ID, AWS_REGION)
PBM_HIPPO_BUCKET = 'etl-pbm-hippo-{}-{}'.format(AWS_ACCOUNT_ID, AWS_REGION)
PBM_HIPPO_EXPORT_PREFIX='exports/'
PBM_HIPPO_EXPORT_HISTORY_PREFIX = 'exports/history/'
PERIOD = 'day'

CUR_DATE = utils.get_current_date()

ENV = {
    'PERIOD': PERIOD,
    'RUN_DATE': "{{ dag_run.conf.get('RUN_DATE') }}", # by default: current_date if not explicitly set via w/ config
    'INTER_PERIOD_FLAG': "False",
    'FINANCIAL_CLAIMS_BUCKET': FINANCIAL_CLAIMS_BUCKET,
    'FINANCIAL_CLAIMS_PREFIX': 'exports/',
    'FINANCIAL_CLAIMS_SCHEMA': 'financial_claims',
    'FINANCIAL_CLAIMS_TEMP_FILES_PREFIX': f'temp/{PERIOD}',
    'PHARMACY_HISTORY_BUCKET': PHARMACY_HISTORY_BUCKET,
    'PHARMACY_HISTORY_PREFIX': 'export/history/',
    'PBM_HIPPO_BUCKET': PBM_HIPPO_BUCKET,
    'PBM_HIPPO_EXPORT_PREFIX': PBM_HIPPO_EXPORT_PREFIX,
    'PBM_HIPPO_EXPORT_HISTORY_PREFIX': PBM_HIPPO_EXPORT_HISTORY_PREFIX,

    'AWS_DEFAULT_REGION': AWS_REGION,
    
    'S3_EXPORTER_ENABLED': 'True',
    'REDSHIFT_EXPORTER_ENABLED': 'no' if utils.get_hippo_env() == 'dev' else 'yes', ## staging and production do have own redshift clusters

    # GoodRx 'synthetic_fee_per_fill' coefficients:
    'NEW_CHANGE_HEALTHCARE_FEE_PERCENTAGE_SPLIT': '0.5',
    'OLD_CHANGE_HEALTHCARE_PER_CLAIM_FEE_DOLLARS': '1.41',
    # GoodRx 'processor_fee_deductable':
    'GOODRX_PROCESSOR_FEE_DEDUCTABLE_CENTS': '12',
    # GoodRx 'partner_margin' standard margin:
    'GOODRX_ABSOLUTE_MIN_MARGIN_DOLLARS': '5.7',
    'GOODRX_MARGIN_PERCENT': '0.9',
    'GOODRX_MARGIN_FOR_WALMART_PERCENT': '0.97',
}

dag = DAG(
    'etl-financial-claims-preprocess_daily',
    default_args=default_args,
    schedule_interval='0 8 * * *',
    max_active_runs=1,
    catchup=False,
)

dag.doc_md = """
    If you want to manually set report date to some date in the past start DAG with w/ config: {"RUN_DATE": "2023-09-02"}
    """

kwargs = {
    'repository_name': 'etl-financial-claims',
    'execution_timeout': timedelta(minutes=60),
    'worker_type': 'G.4X'
}

run_tests = HippoGlueJobOperator(
    task_id='run_tests',
    script_args={**ENV, **{'TASK': 'run_tests'}},
    dag=dag,
    **kwargs
)

run_tests.doc_md = """\
#Run tests before start main task
"""

download_claims = HippoGlueJobOperator(
    task_id='download_claims',
    script_args={**ENV, **{'TASK': 'download_claims'}},
    dag=dag,
    **kwargs
)

download_claims.doc_md = """\
# Download claims for financial_claims_preprocess
"""

download_sources = HippoGlueJobOperator(
    task_id='download_sources',
    script_args={**ENV, **{'TASK': 'download_sources'}},
    dag=dag,
    **kwargs
)

download_sources.doc_md = """\
# Download other sources for financial_claims_preprocess: pharmacy_history, ndc_v2, ndc_cost_v2 etc. 
"""


financial_claims_preprocess = HippoGlueJobOperator(
    task_id='financial_claims_preprocess',
    script_args={**ENV, **{'TASK': 'financial_claims_preprocess'}},
    dag=dag,
    **kwargs
)

financial_claims_preprocess.doc_md = """\
# Create and load `Financial Claims Preprocess` daily dataset. 
"""

        
wipe_temp_data_in_s3 = HippoGlueJobOperator(
    task_id=f'wipe_temp_data_in_s3_all_data',
    script_args={**ENV, **{'TASK': 'wipe_temp_data_in_s3'}},
    dag=dag,
    **kwargs
)

wipe_temp_data_in_s3.doc_md = """\
# Delete all temporal data in s3://etl-financial-claims/temp path. 
"""

run_tests >> download_claims >> download_sources >> financial_claims_preprocess >> wipe_temp_data_in_s3
