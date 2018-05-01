import mock
import unittest
import uosci.uosci_jenkins as uosci_jenkins


class TestModel(unittest.TestCase):
    def setUp(self):
        super(TestModel, self).setUp()

    @mock.patch.object(uosci_jenkins, 'Jenkins')
    def test_matrix_view(self, _jenkins):
        uosci_jenkins.Jenkins(
            'http://127.0.0.1:8080',
            username='test_user',
            password='test_password')
        _jenkins.assert_called_with(
            'http://127.0.0.1:8080',
            username='test_user',
            password='test_password')
