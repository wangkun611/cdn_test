import unittest
from cdn_model_test import FunctionTestCase
import cdn_model_test
import argparse
import xlrd

parser = argparse.ArgumentParser(description='Test CDN backup node')
parser.add_argument("--ip", help="CDN backup node ip", required=True)
parser.add_argument("domain", help="Domain XLS file", nargs='*')

def suite(files):
    suite = unittest.TestSuite()
    for file in files:
        xls = xlrd.open_workbook(file)
        sheet = xls.sheet_by_index(0)
        for row_index in range(1, sheet.nrows):
            domain =  sheet.cell(row_index, 0).value
            url =  sheet.cell(row_index, 1).value
            https =  sheet.cell(row_index, 2).value
            ppi =  sheet.cell(row_index, 3).value
            suite.addTest(FunctionTestCase(domain, url=url, methodName='test_http'))
            if https:
                suite.addTest(FunctionTestCase(domain, url=url, methodName='test_https'))
            if ppi:
                suite.addTest(FunctionTestCase(domain, url=url, methodName='test_ppi'))
    return suite

if __name__ == '__main__':
    args = parser.parse_args()
    cdn_model_test.backupcdn_ip = args.ip

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite(args.domain))
