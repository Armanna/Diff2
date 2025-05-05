from sources.redshift_downloader import FinancialsRedshiftDownloader
from hippo import logger

log = logger.getLogger('claim_processing_fees')

class ClaimsProcFeesSource:
    def __init__(self, period_start, period_end):
        log.info('Using default Redshift credentials')
        self.downloader = FinancialsRedshiftDownloader()
        self.partner_financials_sql = f"""
            SELECT 
                valid_from::timestamp,
                rx_id,
                pbm_fee,
                erx_fee,
                processor_fee
            FROM 
                reporting.claim_processing_fees
            WHERE
                rx_id||valid_from::timestamp IN (
                    SELECT 
                        rx_id||valid_from::timestamp 
                    FROM 
                        reporting.claims
                    WHERE 
                        (valid_to::date >= '{period_start}'::date and valid_to::date <= '{period_end}'::date and fill_status = 'filled')
                        OR
                        (valid_from::date >= '{period_start}'::date and valid_from::date <= '{period_end}'::date and valid_to::date > '{period_end}'::date and fill_status = 'filled')
                )
        """
