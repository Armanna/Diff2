from hippo import logger
from hippo.sources.redshift import RedshiftDownloader
from transforms import utils

log = logger.getLogger('redshift_downloader')

class FinancialsRedshiftDownloader(RedshiftDownloader):

    def pull_claim_processing_fees(self, sql_text):
        claim_processing_fees_df = self.pull(sql_text)
        claim_processing_fees_df['valid_from'] = claim_processing_fees_df['valid_from'].astype('datetime64[ns]')
        claim_processing_fees_df = utils.cast_columns_to_decimal(claim_processing_fees_df, column_names=['erx_fee','processor_fee','pbm_fee'], fillna_flag=True)
        return claim_processing_fees_df

    def pull_goodrx_feed_mac_prices(self, sql_text):
        goodrx_feed_mac_prices_df = self.pull(sql_text)
        goodrx_feed_mac_prices_df[['valid_from','valid_to']] = goodrx_feed_mac_prices_df[['valid_from','valid_to']].astype('datetime64[ns]')
        goodrx_feed_mac_prices_df['ndc11'] = goodrx_feed_mac_prices_df['ndc11'].astype(str).str.zfill(11)
        goodrx_feed_mac_prices_df['price_group'] = goodrx_feed_mac_prices_df['price_group'].astype('int32')
        return goodrx_feed_mac_prices_df

    def pull_rank(self, sql_text):
        rank_df = self.pull(sql_text)
        rank_df['min'] = rank_df['min'].astype('datetime64[ns]')
        return rank_df
    
    def pull_partners(self, sql_text):
        partner_df = self.pull(sql_text)
        partner_df['partner'] = partner_df['partner'].astype(str)
        return partner_df
