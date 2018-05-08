import mock
import unittest
import uosci.uosci_jenkins as uosci_jenkins


class TestModel(unittest.TestCase):
    def setUp(self):
        super(TestModel, self).setUp()

    @mock.patch.object(uosci_jenkins, 'Jenkins')
    def test_init(self, _jenkins):
        uosci_jenkins.Jenkins(
            'http://127.0.0.1:8080',
            username='test_user',
            password='test_password')
        _jenkins.assert_called_with(
            'http://127.0.0.1:8080',
            username='test_user',
            password='test_password',)

    # @mock.patch.object(uosci_jenkins, 'Jenkins')
    @mock.patch("uosci.uosci_jenkins.jenkins.Jenkins.get_jobs")
    def test_matrix_view(self, _get_jobs):
        j_client = mock.MagicMock()
        uosci_jenkins.jenkins.Jenkins = j_client
        client = uosci_jenkins.Jenkins(
            'http://127.0.0.1:8080',
            username='test_user',
            password='test_password')
        # client.get_jobs.return_value = mock.MagicMock()
        client.matrix('test')
        _get_jobs.assert_called_with(view_name='test')
