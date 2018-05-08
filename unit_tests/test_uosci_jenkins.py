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

    def test_get_series_from_url(self):
        result = uosci_jenkins.get_series_from_url(
            'http://jenkins_url/job/job_name/'
            'MOJO_SPEC=specs%2Fstorage%2Fceph%2Fradosgw_ha,'
            'U_OS=trusty-mitaka/26/'
        )
        self.assertEqual(result, 'trusty-mitaka')

    def test_get_series_from_bad_url(self):
        result = uosci_jenkins.get_series_from_url(
            "http://something-else.example.com"
        )
        self.assertIsNone(result)

    def test_update_from_run(self):
        run = {'actions': [
            {},
            {'_class': 'hudson.model.CauseAction',
             'causes': [
                 {
                     '_class': 'hudson.model.Cause$UpstreamCause',
                     'shortDescription': 'Started by upstream '
                     'project '
                     '"test_mojo_ceph_radosgw_ha_master_matrix" '
                     'build number 26',
                     'upstreamBuild': 26,
                     'upstreamProject': 'test_mojo_ceph_radosgw_'
                     'ha_master_matrix',
                     'upstreamUrl': 'job/test_mojo_ceph_radosgw_'
                     'ha_master_matrix/'}]},
            {'_class': 'hudson.plugins.parameterizedtrigger.'
                       'BuildInfoExporterAction'},
            {},
            {},
            {}],
            'artifacts': [],
            'building': False,
            'builtOn': 'osci-task-1',
            'changeSet': {'_class': 'hudson.scm.EmptyChangeLogSet',
                          'items': [],
                          'kind': None},
            'culprits': [],
            'description': None,
            'displayName': '#26',
            'duration': 12492999,
            'estimatedDuration': 15001437,
            'executor': None,
            'fullDisplayName': 'test_mojo_ceph_radosgw_ha_master_matrix - '
            'specs/storage/ceph/radosgw_ha,artful-pike #26',
            'id': '26',
            'keepLog': False,
            'number': 26,
            'queueId': 86278,
            'result': 'FAILURE',
            'timestamp': 1525215901043,
            'url': 'http://10.245.162.49:8080/job/'
                       'test_mojo_ceph_radosgw_ha_master_matrix/'
                       'MOJO_SPEC=specs%2Fstorage%2Fceph%2Fradosgw_ha,'
                       'U_OS=artful-pike/26/'}

        result = uosci_jenkins.result_from_run(run)
        self.assertFalse(result['successful'])
