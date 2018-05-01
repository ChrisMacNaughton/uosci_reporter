import mock
import uosci.mojo as mojo
import unit_tests.utils as ut_utils

import unittest


class TestModel(unittest.TestCase):
    def setUp(self):
        super(TestModel, self).setUp()

    @mock.patch.object(mojo.jenkins, 'matrix')
    def test_main(self, _matrix):
        mojo.main()
        _matrix.assert_called_with('MojoMatrix')
