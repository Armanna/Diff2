import os
from datetime import datetime, timedelta
from airflow import DAG
from lib.operators.glue import HippoGlueJobOperator
from lib.v2 import utils
from dateutil.relativedelta import relativedelta
from airflow.models import Variable

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

## Strings with YYYY-MM-DD format
INITIAL_DATE_STR = Variable.get("etl-financial-claims-iterable-month-initial-date")
END_DATE_STR = Variable.get("etl-financial-claims-iterable-month-end-date") 
DATE_STR_LIST = []

try:
    INITIAL_DATE = datetime.strptime(INITIAL_DATE_STR, "%Y-%m-%d")
    END_DATE = datetime.strptime(END_DATE_STR, "%Y-%m-%d")

except:
    print("Proper start of end dates were not provided")
    INITIAL_DATE = datetime.strptime('2024-01-01', "%Y-%m-%d")
    END_DATE = datetime.strptime('2024-02-01', "%Y-%m-%d")

NUM_MONTHS = (END_DATE.year - INITIAL_DATE.year) * 12 + (END_DATE.month - INITIAL_DATE.month)

DATE_STR_LIST = [(INITIAL_DATE + relativedelta(months=x)).replace(day=1).strftime("%Y-%m-%d") for x in range(NUM_MONTHS + 1)]

dag = DAG(
    'etl-financial-claims-preprocess_monthly_iterable',
    default_args=default_args,
    max_active_runs=1,
    catchup=False,
    schedule_interval=None,
    is_paused_upon_creation=True,
)

pipeline_list = []

for i, SINGLE_DATE in enumerate(DATE_STR_LIST):
    ENV = {
        'PERIOD': 'month',
        'RUN_DATE': SINGLE_DATE, 
        'INTER_PERIOD_FLAG': "False",
        'FINANCIAL_CLAIMS_BUCKET': FINANCIAL_CLAIMS_BUCKET,
        'FINANCIAL_CLAIMS_PREFIX': 'exports/',
        'FINANCIAL_CLAIMS_SCHEMA': 'financial_claims',
        'FINANCIAL_CLAIMS_TEMP_FILES_PREFIX': 'temp/',
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



    dag.doc_md = """
        If you want to manually set report date to some date in the past start DAG with w/ config: {"INITIAL_DATE": "2023-09-01", "END_DATE": "2023-10-01"}
        """

    kwargs = {
        'repository_name': 'etl-financial-claims',
        'execution_timeout': timedelta(minutes=90),
        'worker_type': 'G.4X'
    }

    if i == 0:      ## Only run the test task and download claims once
        run_tests = HippoGlueJobOperator(
            task_id=f'run_tests_{SINGLE_DATE}',
            script_args={**ENV, **{'TASK': 'run_tests'}},
            dag=dag,
            **kwargs
        )

        run_tests.doc_md = """\
        #Run tests before start main task
        """
        
    else:
        pass

    download_claims = HippoGlueJobOperator(
        task_id=f'download_claims_{SINGLE_DATE}',
        script_args={**ENV, **{'TASK': 'download_claims'}},
        dag=dag,
        **kwargs
    )

    download_claims.doc_md = """\
    # Download claims for financial_claims_preprocess
    """
    
    download_sources = HippoGlueJobOperator(
        task_id=f'download_sources_{SINGLE_DATE}',
        script_args={**ENV, **{'TASK': 'download_sources'}},
        dag=dag,
        **kwargs
    )

    download_sources.doc_md = """\
    # Download other sources for financial_claims_preprocess: pharmacy_history, ndc_v2, ndc_cost_v2 etc. 
    """


    financial_claims_preprocess = HippoGlueJobOperator(
        task_id=f'financial_claims_preprocess_{SINGLE_DATE}',
        script_args={**ENV, **{'TASK': 'financial_claims_preprocess'}},
        dag=dag,
        **kwargs
    )

    financial_claims_preprocess.doc_md = """\
    # Create and load `Financial Claims Preprocess` monthly dataset. 
    """

    wipe_temp_data_in_s3 = HippoGlueJobOperator(
        task_id=f'wipe_temp_data_in_s3_all_data_{SINGLE_DATE}',
        script_args={**ENV, **{'TASK': 'wipe_temp_data_in_s3'}},
        dag=dag,
        **kwargs
    )

    wipe_temp_data_in_s3.doc_md = """\
    # Delete all temporal data in s3://etl-financial-claims/temp path. 
    """
    
    pipeline_list.append(download_claims)
    pipeline_list.append(download_sources)
    pipeline_list.append(financial_claims_preprocess)
    pipeline_list.append(wipe_temp_data_in_s3)


for i, task in enumerate(pipeline_list):
    if i == 0:      ## Adding as run_tests as first task to complete
        run_tests >> task

    else:           ## Appending to the pipeline the rest of tasks
        pipeline_list[i-1] >> pipeline_list[i]
        