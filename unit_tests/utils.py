# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Note that the unit_tests/__init__.py also mocks out two charmhelpers imports
# that have side effects that try to apt install modules:
# sys.modules['charmhelpers.contrib.openstack.utils'] = mock.MagicMock()
# sys.modules['charmhelpers.contrib.network.ip'] = mock.MagicMock()

import contextlib
import io
import mock
import unittest


@contextlib.contextmanager
def patch_open():
    '''Patch open() to allow mocking both open() itself and the file that is
    yielded.

    Yields the mock for "open" and "file", respectively.'''
    mock_open = mock.MagicMock(spec=open)
    mock_file = mock.MagicMock(spec=io.FileIO)

    @contextlib.contextmanager
    def stub_open(*args, **kwargs):
        mock_open(*args, **kwargs)
        yield mock_file

    with mock.patch('builtins.open', stub_open):
        yield mock_open, mock_file
