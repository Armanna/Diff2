import unittest
import os
import sys

from hippo import logger

lib_path = os.path.abspath('.')
sys.path.append(lib_path)
from transforms.utils import process_report_dates, parse_current_report_day

log = logger.getLogger('period_test')

class TestPeriod(unittest.TestCase):
    def setUp(self):
        log.info('Set up variables')
        self.period = None
        self.inter_period_flag = None
        self.curdate = None

    def test_1_weekly(self):
        log.info('TEST 1 Started! Period - "week". Run date set manually to some date in the past. Process data for the previous week.')
        self.period = 'week'
        self.curdate = '2023-09-27'

        input_date = parse_current_report_day(self.curdate)
        current_report_date, previous_report_date, current_month = process_report_dates(self.period, input_date)
        self.assertEqual(current_report_date, '2023-09-18')
        self.assertEqual(previous_report_date, '2023-09-11')
        self.assertEqual(current_month, '2023-09-01')

    def test_2_weekly(self):
        log.info('TEST 2 Started! Period - "week". Run date is not set. Process data for the previous week.')
        self.period = 'week'
        self.curdate = "2023-10-06"

        input_date = parse_current_report_day(self.curdate)
        current_report_date, previous_report_date, current_month = process_report_dates(self.period, input_date)
        self.assertEqual(current_report_date, '2023-09-25')
        self.assertEqual(previous_report_date, '2023-09-18')
        self.assertEqual(current_month, '2023-09-01')

    def test_1_monthly(self):
        log.info('TEST 4 Started! Period - "month". Run date set manually to some date in the past. Default run - process data for the previous month')
        self.period = 'month'
        self.curdate = '2023-09-12'

        input_date = parse_current_report_day(self.curdate)
        current_report_date, previous_report_date, current_month = process_report_dates(self.period, input_date)
        self.assertEqual(current_report_date, '2023-08-01')
        self.assertEqual(previous_report_date, '2023-07-01')
        self.assertEqual(current_month, '2023-09-01')

    def test_2_monthly(self):
        log.info('TEST 5 Started! Period - "month".  Run date is not set. Default run - process data for the previous month')
        self.period = 'month'
        self.curdate = '2023-10-06'

        input_date = parse_current_report_day(self.curdate)
        current_report_date, previous_report_date, current_month = process_report_dates(self.period, input_date)
        self.assertEqual(current_report_date, '2023-09-01')
        self.assertEqual(previous_report_date, '2023-08-01')
        self.assertEqual(current_month, '2023-10-01')

    def test_3_monthly(self):
        log.info('TEST 6 Started! Period - "month".  Run date is not set. Inter period flag is turn on - process data for the current month')
        self.period = 'month'
        self.curdate = '2023-10-06'
        self.inter_period_flag = True
        
        input_date = parse_current_report_day(self.curdate)
        current_report_date, previous_report_date, current_month = process_report_dates(self.period, input_date, inter_period_flag=self.inter_period_flag)
        self.assertEqual(current_report_date, '2023-10-16')
        self.assertEqual(previous_report_date, '2023-09-16')
        self.assertEqual(current_month, '2023-10-01')


if __name__ == '__main__':
    unittest.main()
