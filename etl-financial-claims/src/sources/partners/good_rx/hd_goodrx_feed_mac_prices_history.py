from sources.redshift_downloader import FinancialsRedshiftDownloader
from hippo import logger

log = logger.getLogger('goodrx_feed_mac_prices_history')

class GoodrxFeedMacSource:
    def __init__(self, period_start, period_end):
        log.info('Using default Redshift credentials')
        self.downloader = FinancialsRedshiftDownloader()
        self.partner_financials_sql = f"""
            SELECT 
                price_group,
                ndc11,
                valid_from::timestamp,
                replace(valid_to::text, '2300.01.01T00:00:00', '2050-01-01 00:00:00')::timestamp as valid_to 
            FROM 
                historical_data.goodrx_feed_mac_prices_history
            WHERE ndc11 IN (
                SELECT 
                    product_id
                FROM 
                    reporting.claims
                WHERE
                    (valid_to::date >= '{period_start}'::date and valid_to::date <= '{period_end}'::date and fill_status = 'filled')
                    OR
                    (valid_from::date >= '{period_start}'::date and valid_from::date <= '{period_end}'::date and valid_to::date > '{period_end}'::date and fill_status = 'filled')
                )
        """
