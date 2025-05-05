from io import BytesIO

import sources.claims as claims
from transforms import utils
from hippo.exporters import Registry
from hippo.exporters import s3 as s3_exporter
from hippo.sources import claims_downloader
from hippo.sources.claims import FillsAndReversals, BasisOfReimbursment, FillStatus, Partners
from hippo import logger

log = logger.getLogger('download_claims.py')

def run(financial_claims_bucket, financial_claims_temp_files_prefix, **kwargs):
    log.info(f"\nDeleting data in:")
    log.info(f"Bucket: \n {financial_claims_bucket}")
    log.info(f"Prefix: \n {financial_claims_temp_files_prefix}")

    wipe = s3_exporter.S3Exporter(financial_claims_bucket, financial_claims_temp_files_prefix)
    wipe._wipe()
