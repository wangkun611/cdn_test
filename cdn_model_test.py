from unittest import TestCase
from unittest.util import strclass
from urllib3.util import connection
from difflib import SequenceMatcher
import requests
import re

use_backupcdn = False
backupcdn_ip=''
_orig_create_connection = connection.create_connection
def patched_create_connection(address, *args, **kwargs):
    """Wrap urllib3's create_connection to resolve the name elsewhere"""
    # resolve hostname to an ip address; use your own
    # resolver here, as otherwise the system resolver will be used.
    host, port = address
    if use_backupcdn:
        host = backupcdn_ip

    return _orig_create_connection((host, port), *args, **kwargs)

connection.create_connection = patched_create_connection

class FunctionTestCase(TestCase):
    """A test case that wraps a test function.
    This is useful for slipping pre-existing test functions into the
    unittest framework. Optionally, set-up and tidy-up functions can be
    supplied. As with TestCase, the tidy-up ('tearDown') function will
    always be called if the set-up ('setUp') function ran successfully.
    """

    def __init__(self, domain, url = None, methodName='runTest', setUp=None, tearDown=None, description=None):
        super(FunctionTestCase, self).__init__(methodName)
        self._setUpFunc = setUp
        self._tearDownFunc = tearDown
        self._description = description
        self._domain = domain
        self._url = url

    def setUp(self):
        if self._setUpFunc is not None:
            self._setUpFunc()

    def tearDown(self):
        if self._tearDownFunc is not None:
            self._tearDownFunc()

    def get_test_url(self, https=False):
        if not self._url:
            return ('https' if https else 'http') + '://' + self._domain + '/'
        if https:
            return re.sub(r'^http', 'https', self._url)
        return self._url

    def test_http(self):
        global use_backupcdn
        url = self.get_test_url()
        headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

        use_backupcdn = False
        r1 = requests.get(url, headers=headers, allow_redirects=False)

        use_backupcdn = True
        r2 = requests.get(url, headers=headers, allow_redirects=False)
        self.assertEqual(r1.status_code, r2.status_code)
        if hash(r1.text) == hash(r2.text):
            self.assertTrue(True)
            return

        self.assertGreater(SequenceMatcher(a=r1.text, b=r2.text).ratio(), 0.8, 'content is not match')

    def test_https(self):
        global use_backupcdn
        url = self.get_test_url(True)
        headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

        try:
            use_backupcdn = False
            r1 = requests.get(url, headers=headers, allow_redirects=False)
        except requests.exceptions.SSLError as err:
            self.skipTest('domain not support https')
            return

        try:
            use_backupcdn = True
            r2 = requests.get(url, headers=headers, allow_redirects=False)
        except requests.exceptions.SSLError as err:
            pass

        self.assertEqual(r1.status_code, r2.status_code)
        if hash(r1.text) == hash(r2.text):
            self.assertTrue(True)
            return

        self.assertGreater(SequenceMatcher(a=r1.text, b=r2.text).ratio(), 0.8, 'content is not match')

    def test_ppi(self):
        pass

    def runTest(self):
        pass

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self._setUpFunc == other._setUpFunc and \
               self._tearDownFunc == other._tearDownFunc and \
               self._domain == other._domain and \
               self._description == other._description

    def __hash__(self):
        return hash((type(self), self._setUpFunc, self._tearDownFunc,
                     self._domain, self._description))

    def __str__(self):
        return "%s (%s)" % (self._testMethodName,
                            self._domain)

    def __repr__(self):
        return "<%s tec=%s>" % (strclass(self.__class__),
                                     self._domain)

#    def shortDescription(self):
#        if self._description is not None:
#            return self._description
#        return self._domain
#        return doc and doc.split("\n")[0].strip() or None
