#!/usr/bin/env python3
from hippo import reload_files_for_glue
reload_files_for_glue()

import click
import sys
import unittest

from transforms import utils
from tasks import download_claims, download_other_sources, wipe_temp_data_in_s3

from tasks import financial_claims_preprocess
from hippo import logger
from hippo.dags.lib.v2 import secrets

log = logger.getLogger('app.py')

@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
))
@click.option('--task', help='task to run')
@click.option("--period", envvar="PERIOD")
@click.option("--inter-period-flag", envvar="INTER_PERIOD_FLAG", default=None)
@click.option("--run-date", envvar="RUN_DATE", default=None)
@click.option("--to-emails", envvar="TO_EMAILS")
@click.option("--s3-exporter-enabled", envvar="S3_EXPORTER_ENABLED", default=True, type=click.BOOL)
@click.option("--redshift-exporter-enabled", envvar="REDSHIFT_EXPORTER_ENABLED", default=False, type=click.BOOL)
@click.option("--email-exporter-enabled", envvar="EMAIL_EXPORTER_ENABLED", default=True, type=click.BOOL)
@click.option("--slack-channel", envvar='SLACK_CHANNEL', default='C07M2C1EQMD')
@click.option("--slack-bot-token", envvar='SLACK_BOT_TOKEN', default=secrets.read_aws_parameter("/terraform/etl-runtime-config/SLACK_BOT_TOKEN"))
@click.option("--pharmacy-history-bucket", envvar="PHARMACY_HISTORY_BUCKET")
@click.option("--pharmacy-history-prefix", envvar="PHARMACY_HISTORY_PREFIX")
@click.option("--pbm-hippo-bucket", envvar="PBM_HIPPO_BUCKET")
@click.option("--pbm-hippo-export-prefix", envvar="PBM_HIPPO_EXPORT_PREFIX")
@click.option("--pbm-hippo-export-history-prefix", envvar="PBM_HIPPO_EXPORT_HISTORY_PREFIX")
@click.option("--financial-claims-bucket", envvar="FINANCIAL_CLAIMS_BUCKET")
@click.option("--financial-claims-prefix", envvar="FINANCIAL_CLAIMS_PREFIX")
@click.option("--financial-claims-schema", envvar="FINANCIAL_CLAIMS_SCHEMA")
@click.option("--financial-claims-temp-files-prefix", envvar="FINANCIAL_CLAIMS_TEMP_FILES_PREFIX")
@click.option("--new-change-healthcare-fee-percentage-split", envvar="NEW_CHANGE_HEALTHCARE_FEE_PERCENTAGE_SPLIT")
@click.option("--old-change-healthcare-per-claim-fee-dollars", envvar="OLD_CHANGE_HEALTHCARE_PER_CLAIM_FEE_DOLLARS")
@click.option("--goodrx-margin-percent", envvar="GOODRX_MARGIN_PERCENT")
@click.option("--goodrx-absolute-min-margin-dollars", envvar="GOODRX_ABSOLUTE_MIN_MARGIN_DOLLARS")
@click.option("--goodrx-processor-fee-deductable-cents", envvar="GOODRX_PROCESSOR_FEE_DEDUCTABLE_CENTS")
@click.option("--goodrx-margin-for-walmart-percent", envvar="GOODRX_MARGIN_FOR_WALMART_PERCENT")
@click.option("--partner-margin-famulus", envvar="PARTNER_MARGIN_FAMULUS")

def main(task, **kwargs):
    processed_kwargs=utils.process_airflow_config_variables(**kwargs)
    if task == 'run_tests':
        test_loader = unittest.TestLoader()
        test_suite = test_loader.discover('test', pattern='test_*.py')
        unittest.TextTestRunner().run(test_suite)
    elif task == 'financial_claims_preprocess':
        financial_claims_preprocess.run(**processed_kwargs)
    elif task == 'download_claims':
        download_claims.run(**processed_kwargs)
    elif task == 'download_sources':
        download_other_sources.run(**processed_kwargs)
    elif task == 'wipe_temp_data_in_s3':
        wipe_temp_data_in_s3.run(**processed_kwargs)
    else:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except SystemExit as e:
        if e.code != 0:
            raise
