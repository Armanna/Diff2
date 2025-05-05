from sources.redshift_downloader import FinancialsRedshiftDownloader
from hippo import logger

log = logger.getLogger('all_partners')

class AllPartners:
    def __init__(self):
        log.info('Using default Redshift credentials')
        self.downloader = FinancialsRedshiftDownloader()
        self.partner_financials_sql = f"""
            SELECT DISTINCT cr.partner FROM reporting.cardholders cr
        """
