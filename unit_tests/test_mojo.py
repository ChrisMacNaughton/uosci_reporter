import mock
import unittest
import uosci_reporter.mojo as mojo


class TestModel(unittest.TestCase):
    def setUp(self):
        super(TestModel, self).setUp()

    @mock.patch.object(mojo, 'execute')
    def test_call_main(self, _execute):
        old_sys_argv = mojo.sys.argv
        mojo.sys.argv = [old_sys_argv[0]] + \
            ['-u', 'test', '-p', 'test-pass', '-g', 'creds.json']
        try:
            mojo.main()
        finally:
            mojo.argv = old_sys_argv
        _execute.assert_called_with(
            credentials='creds.json',
            filter=None,
            host='http://10.245.162.49:8080',
            password='test-pass',
            sheet='https://docs.google.com/spreadsheets/d/1d31P5Qu_nP'
                  '__gCsoy4u6egpSnG34bMjpVijKtlJSmLU',
            username='test')

    @mock.patch.object(mojo, 'execute')
    def test_filter(self, _execute):
        old_sys_argv = mojo.sys.argv
        mojo.sys.argv = [old_sys_argv[0]] + \
            ['-u', 'test', '-p', 'test-pass', '-f',
             'test_stuff', '-g', '/home/test/creds.json']
        try:
            mojo.main()
        finally:
            mojo.argv = old_sys_argv
        _execute.assert_called_with(
            credentials='/home/test/creds.json',
            filter='test_stuff',
            host='http://10.245.162.49:8080',
            password='test-pass',
            sheet='https://docs.google.com/spreadsheets/d/1d31P5Qu_nP'
                  '__gCsoy4u6egpSnG34bMjpVijKtlJSmLU',
            username='test')

    @mock.patch.object(mojo.uosci_jenkins, 'Jenkins')
    def test_fetch_results(self, _jenkins):
        client = mock.MagicMock()
        _jenkins.return_value = client
        client.matrix.return_value = [{
            'name': 'test'
        }]
        mojo.fetch_results(
            host='http://127.0.0.1:8080',
            username='test_user',
            password='test_password'
        )
        _jenkins.assert_called_with(
            'http://127.0.0.1:8080',
            username='test_user',
            password='test_password')
        client.matrix.assert_called_with('MojoMatrix')

    def test_parser(self):
        args = mojo.parse_args([
            '-u', 'test_user',
            '-p', 'supersecret',
            '-g', 'creds.json'])
        self.assertEqual(args.username, 'test_user')
        self.assertEqual(args.password, 'supersecret')
        self.assertEqual(args.host, 'http://10.245.162.49:8080')
        self.assertEqual(args.google_credentials, 'creds.json')

    @mock.patch.object(mojo.uosci_jenkins, 'Jenkins')
    def test_fetch_results_with_filter(self, _jenkins):
        client = mock.MagicMock()
        _jenkins.return_value = client
        client.matrix.return_value = [{
            'name': 'testing stuff'
        }]
        mojo.fetch_results(
            host='http://127.0.0.1:8080',
            username=None,
            password=None,
            filter='testing',
        )

    def test_filter_job_name_with_test(self):
        self.assertFalse(mojo.filter_job("test_something"))
        self.assertTrue(mojo.filter_job("not-included"))

    def test_filter_job_name_with_filter(self):
        self.assertFalse(mojo.filter_job("test_something"))
        self.assertTrue(mojo.filter_job("test_something", "else"))

    # def test_col_id_to_letter(self):
    #     self.assertEqual(mojo.col_id_to_letter(2), 'B')
    #     self.assertEqual(mojo.col_id_to_letter(10), 'J')
    #     self.assertEqual(mojo.col_id_to_letter(26), 'Z')
