import mock
import uosci.jenkins as jenkins
import unit_tests.utils as ut_utils

import unittest

class TestModel(unittest.TestCase):
    def setUp(self):
        super(TestModel, self).setUp()
    
    @mock.patch.object(jenkins.jenkins, 'Jenkins')
    def test_client_setup(self, _jenkins):
        client = jenkins.client(username='test_user', password='test_password')
        _jenkins.assert_called_with(
            'http://10.245.162.49:8080', username='test_user', password='test_password')

    def test_matrix_view(self):
        client = mock.MagicMock()
        client.get_jobs.return_value = [
            {
                '_class': 'hudson.model.FreeStyleProject',
                'name': 'test_job',
                'url': 'http://127.0.0.1:8080/job/test_job/',
                'color': 'blue',
                'fullname': 'test_job'
            }]
        jobs = jenkins.matrix(client, 'MojoMatrix')
        client.get_jobs.assert_called_with(view_name='MojoMatrix')
        self.assertEqual(len(jobs), 1)
