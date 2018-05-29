from collections import namedtuple
import mock
import unittest
import uosci_reporter.mojo as mojo
from datetime import datetime, timezone


Position = namedtuple('position', ['row', 'col'], verbose=True)


class TestModel(unittest.TestCase):
    def setUp(self):
        super(TestModel, self).setUp()
        self.row = {'artful-pike': {
            'successful': True,
            'state': 'Pass',
            'url': 'http:path/to/jenkins',
            'date': datetime.fromtimestamp(1525215901043 / 1000,
                                           tz=timezone.utc),
            'name': 'test_mojo_ha_oneshot_master_matrix',
            'spec': 'specs/full_stack/ha_oneshot',
        }}

        self.test_config = {
            'jenkins': {
                'host': 'http://10.245.162.49:8080',
                'username': 'test',
                'password': 'test-pass',
            },
            'google': {
                'sheet': 'https://docs.google.com/spreadsheets/d/'
                         '1w7fTyG9BcAXKezEJLmNluy5POEt0H-n4ny3a17Q4Tnc',
                'credentials': 'creds.json',
            },
        }

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
            config=self.test_config,
            filter=None)

    @mock.patch.object(mojo, 'execute')
    def test_filter(self, _execute):
        old_sys_argv = mojo.sys.argv
        mojo.sys.argv = [old_sys_argv[0]] + \
            ['-u', 'test', '-p', 'test-pass', '-f',
             'test_stuff', '-g', 'creds.json']
        try:
            mojo.main()
        finally:
            mojo.argv = old_sys_argv
        _execute.assert_called_with(
            filter='test_stuff',
            config=self.test_config)

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

    def test_get_job_name_from_specs(self):
        specs = mojo.get_spec_summary(
            {'test_mojo_ha_oneshot_master_matrix': self.row})
        self.assertEqual(
            specs['specs/full_stack/ha_oneshot'],
            'test_mojo_ha_oneshot_master_matrix')

    def test_get_job_from_specs(self):
        specs = {
            'specs/full_stack/ha_oneshot': 'test_mojo_ha_oneshot_master_matrix'
        }
        res = mojo.get_job_from_specs('specs/full_stack/ha_oneshot', specs)
        self.assertEqual(res, 'test_mojo_ha_oneshot_master_matrix')
        self.assertIsNone(mojo.get_job_from_specs('Spec/Bundle/Test', specs))
        self.assertIsNone(mojo.get_job_from_specs('', specs))
        self.assertIsNone(mojo.get_job_from_specs('NoResult', specs))

    def test_cell_for_row(self):
        self.assert_cell_value(
            2,
            11,
            '=HYPERLINK("http:path/to/jenkins","01-May - Pass")')

    def test_cell_for_row_empty_job(self):
        self.assert_cell_value(2, 10, 'NA')

    def assert_cell_value(self, row, col, value):
        cell = mojo.cell_for_row(column_id=col, row_id=row, run=self.row)
        self.assert_cell(cell, Position(row, col+1), value)

    def assert_cell(self, cell, position, value):
        self.assertEqual(cell.row, position.row)
        self.assertEqual(cell.col, position.col)
        self.assertEqual(cell.value, value)
