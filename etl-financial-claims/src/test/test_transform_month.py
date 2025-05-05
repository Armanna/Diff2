import pandas as pd
import unittest
from transforms.transform_partner_financials import _check_dates_reliability

# The test based on unittest module
class TestDates(unittest.TestCase):
    def runTest(self):
        period = 'month'
        current_period_df = pd.DataFrame(data={period: ['2023-01-01','2022-12-01','2022-10-01']})
        last_period_df = pd.DataFrame(data={period: ['2022-11-01','2022-09-01','2022-11-01']})
        last_period_df[period] = last_period_df[period].astype('datetime64[ns]')
        current_period_df[period] = current_period_df[period].astype('datetime64[ns]')
        partner_financials_bucket = 'etl-partner-financials-655141976367-us-east-1'
        previous_report_date = '2023-01-09'
        
        with self.assertRaises(Exception):
            _check_dates_reliability(current_period_df, last_period_df, period, previous_report_date, partner_financials_bucket)

# run the test
if __name__ == '__main__':
    unittest.main()
