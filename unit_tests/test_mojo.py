import mock
import uosci_reporter.mojo as mojo
import unit_tests.utils as ut_utils


class TestModel(ut_utils.BaseTestCase):
    def setUp(self):
        super(TestModel, self).setUp()

    def test_mojo_matrix_view(self):
        client = mock.MagicMock()
        client.get_jobs.return_value = [{'_class': 'hudson.model.FreeStyleProject', 'name': 'test_job',
                                         'url': 'http://127.0.0.1:8080/job/test_job/', 'color': 'blue', 'fullname': 'test_job'}]
        jobs = mojo.mojo_matrix(client)
        client.get_jobs.assert_called_with(view_name='MojoMatrix')
        self.assertEqual(len(jobs), 1)
