from sources.redshift_downloader import FinancialsRedshiftDownloader
from hippo import logger

log = logger.getLogger('rank')

class RankSource:
    def __init__(self, period_start, period_end, period):
        log.info('Using default Redshift credentials')
        self.downloader = FinancialsRedshiftDownloader()
        self.partner_financials_sql = f"""
            SELECT 
                cl.first_name||cl.last_name||cl.date_of_birth as user, 
                min(cl.valid_from::timestamp)
            FROM 
                reporting.claims cl
            WHERE 
                cl.first_name||cl.last_name||cl.date_of_birth in (
                    SELECT 
                        first_name||last_name||date_of_birth as user
                    FROM 
                        reporting.claims
                    where 
                        (valid_to::date >= '{period_start}'::date and valid_to::date <= '{period_end}'::date and fill_status = 'filled')
                        OR
                        (valid_from::date >= '{period_start}'::date and valid_from::date <= '{period_end}'::date and valid_to::date > '{period_end}'::date and fill_status = 'filled')
                    )
                and cl.fill_status = 'filled'
                and cl.valid_to > dateadd('{period}',1,date_trunc('{period}',cl.valid_from))
            GROUP by cl.first_name||cl.last_name||cl.date_of_birth
        """
