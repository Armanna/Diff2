import unittest
import os
import sys
from hippo import logger

lib_path = os.path.abspath('.')
sys.path.append(lib_path)
from transforms.utils import parse_inter_period_flag, parse_current_report_day

log = logger.getLogger('period_test')

class TestPeriod(unittest.TestCase):
    def setUp(self):
        log.info('Set up vairables')
        self.period = None
        self.inter_period_flag = 'None'
        self.run_date = None

    def test_1_mothly(self):
        log.info('TEST 1 Started! Period - month. inter_period_flag is None. Run date is 16th of the month')
        self.period = 'month'
        self.inter_period_flag = 'None'
        self.run_date = '2023-09-16'

        input_date = parse_current_report_day(self.run_date)
        inter_period_flag = parse_inter_period_flag(self.inter_period_flag, input_date, self.period)
        self.assertEqual(inter_period_flag['status'], True)    

    def test_2_mothly(self):
        log.info('TEST 2 Started! Period - month. inter_period_flag is True.')
        self.period = 'month'
        self.inter_period_flag = 'True'
        self.run_date = None

        input_date = parse_current_report_day(self.run_date)
        inter_period_flag = parse_inter_period_flag(self.inter_period_flag, input_date, self.period)
        self.assertEqual(inter_period_flag['status'], True)

    def test_3_mothly(self):
        log.info('TEST 3 Started! Run date is some date in the past. Period - month. inter_period_flag is None.')
        self.period = 'month'
        self.inter_period_flag = 'None'
        self.run_date = "2023-09-06"

        input_date = parse_current_report_day(self.run_date)
        inter_period_flag = parse_inter_period_flag(self.inter_period_flag, input_date, self.period)
        self.assertEqual(inter_period_flag['status'], False)


    def test_1_weekly(self):
        log.info('TEST 4 Started! Period - week. inter_period_flag is None.')
        self.period = 'week'
        self.inter_period_flag = 'None'
        self.run_date = None

        input_date = parse_current_report_day(self.run_date)
        inter_period_flag = parse_inter_period_flag(self.inter_period_flag, input_date, self.period)
        self.assertEqual(inter_period_flag['status'], False)

    def test_2_weekly(self):
        log.info('TEST 5 Started! Period - week. inter_period_flag is True.')
        self.period = 'week'
        self.inter_period_flag = 'True'
        self.run_date = None

        input_date = parse_current_report_day(self.run_date)
        inter_period_flag = parse_inter_period_flag(self.inter_period_flag, input_date, self.period)
        self.assertEqual(inter_period_flag['status'], True)

    def test_3_weekly(self):
        log.info('TEST 6 Started! Period - week. inter_period_flag is None. System day = 16')
        self.period = 'week'
        self.inter_period_flag = 'None'
        self.run_date = '2023-09-16' # check inter_period_flag if period week and day == 16
        
        input_date = parse_current_report_day(self.run_date)
        inter_period_flag = parse_inter_period_flag(self.inter_period_flag, input_date, self.period)
        self.assertEqual(inter_period_flag['status'], False)

if __name__ == '__main__':
    unittest.main()
