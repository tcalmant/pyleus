import pytest
try:
    import venv
    _ = venv # pyflakes
except ImportError:
    pytest.skip("venv module is missing")

import os
import subprocess
import tempfile

from pyleus import exception
from pyleus.cli import venv_proxy
from pyleus.cli.venv_proxy import VirtualenvProxy
from pyleus.testing import mock, builtins

VENV_PATH = tempfile.mkdtemp(prefix="pyleus_venv_")
PYPI_URL = "http://pypi-ninja.ninjacorp.com/simple"


class TestVirtualenvProxyTopLevelFunctions(object):

    @mock.patch.object(subprocess, 'Popen', autospec=True)
    def test__exec_bash_cmd(self, mock_popen):
        mock_proc = mock.Mock()
        mock_popen.return_value = mock_proc
        mock_proc.communicate.return_value = ["baz", "qux"]
        mock_proc.returncode = 1
        with pytest.raises(exception.VirtualenvError) as exc_info:
            venv_proxy._exec_shell_cmd(
                "bash_ninja",
                stdout=42,
                stderr=666,
                err_msg="bar",
            )

        assert "bar" in str(exc_info.value)
        mock_popen.assert_called_once_with(
            "bash_ninja", stdout=42, stderr=666)
        mock_proc.communicate.assert_called_once_with()


class TestVirtualenvProxyCreation(object):

    @mock.patch.object(builtins, 'open', autospec=True)
    @mock.patch.object(VirtualenvProxy, '_create_virtualenv', autospec=True)
    def test___init__(self, mock_create, mock_open):
        mock_open.return_value = 42
        venv = VirtualenvProxy(VENV_PATH, verbose=False)
        mock_open.assert_called_once_with(os.devnull, "w")
        assert venv._out_stream == 42
        mock_create.assert_called_once_with(venv)

        venv = VirtualenvProxy(VENV_PATH, verbose=True)
        assert mock_open.call_count == 1
        assert venv._out_stream is None


def get_pip():
    if os.name == 'nt':
        return os.path.join(VENV_PATH, 'Scripts', 'pip.exe')
    else:
        return os.path.join(VENV_PATH, 'bin', 'pip')


class TestVirtualenvProxyMethods(object):

    @pytest.fixture(autouse=True)
    @mock.patch.object(builtins, 'open', autospec=True)
    @mock.patch.object(VirtualenvProxy, '_create_virtualenv', autospec=True)
    def setup_virtualenv(self, mock_create, mock_open):
        self.venv = VirtualenvProxy(VENV_PATH,
                                    pypi_index_url=PYPI_URL,
                                    verbose=False)

    @mock.patch.object(venv_proxy, '_exec_shell_cmd', autospec=True)
    def test_install_package(self, mock_cmd):
        self.venv.install_package("Ninja==7.7.7")
        mock_cmd.assert_called_once_with(
            [
                get_pip(), "install", "Ninja==7.7.7",
                "-i", PYPI_URL,
                '--use-wheel',
            ],
            stdout=self.venv._out_stream,
            stderr=self.venv._err_stream,
            err_msg=mock.ANY
        )

    @mock.patch.object(venv_proxy, '_exec_shell_cmd', autospec=True)
    def test_install_from_requirements(self, mock_cmd):
        self.venv.install_from_requirements("foo.txt")
        mock_cmd.assert_called_once_with(
            [
                get_pip(), "install",
                "-r", "foo.txt",
                "-i", PYPI_URL,
                '--use-wheel',
            ],
            stdout=self.venv._out_stream,
            stderr=self.venv._err_stream,
            err_msg=mock.ANY
        )
