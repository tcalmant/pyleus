#!/usr/bin/env python
# -- Content-Encoding: UTF-8 --
"""

:author: Thomas Calmant
:copyright: Copyright 2015, Thomas Calmant
:license: Apache License 2.0

..
    Copyright 2015 Thomas Calmant
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
        http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import os
import subprocess
import sys
import venv

from pyleus.exception import VirtualenvError

# ------------------------------------------------------------------------------

# Module version
__version_info__ = (0, 0, 1)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
__docformat__ = "restructuredtext en"

# ------------------------------------------------------------------------------


def to_str(data, encoding=None):
    """
    Converts the given input to a string
    """
    if data is None:
        return
    elif isinstance(data, str):
        return data

    if encoding:
        return data.decode(encoding)
    elif os.name == 'nt':
        return data.decode('windows-1252')
    else:
        return data.decode('utf-8')


def _exec_shell_cmd(cmd, stdout, stderr, err_msg):
    """Execute a shell command, returning the output

    If the call has a non-zero return code, raise an VirtualenvError with
    err_msg.
    """
    proc = subprocess.Popen(cmd, stdout=stdout, stderr=stderr)
    out_data, _ = proc.communicate()
    if proc.returncode != 0:
        raise VirtualenvError(err_msg)
    return to_str(out_data)


class VirtualenvProxy(object):
    """Object representing a ready-to-use virtualenv, based on venv"""

    def __init__(self, path,
                 system_site_packages=False,
                 pypi_index_url=None,
                 use_wheel=True,
                 python_interpreter=None,
                 verbose=False):
        """Creates the virtualenv with the options specified"""
        self.path = path
        self._system_site_packages = system_site_packages
        self._pypi_index_url = pypi_index_url
        self._use_wheel = use_wheel
        self._python_interpreter = python_interpreter

        self._verbose = verbose
        self._out_stream = None
        if not self._verbose:
            self._out_stream = open(os.devnull, "w")
        self._err_stream = subprocess.STDOUT

        self._create_virtualenv()

    def _create_virtualenv(self):
        """Creates the actual virtualenv"""
        builder = venv.EnvBuilder(
            system_site_packages=self._system_site_packages, with_pip=True)

        # The builder uses sys.executable to get the interpreter of the virtual
        # environment, so we have to trick it
        backup_exe = None
        if self._python_interpreter:
            backup_exe = sys.executable
            sys.executable = self._python_interpreter

        try:
            builder.create(self.path)
        finally:
            if backup_exe:
                # Get back on track
                sys.executable = backup_exe

    def _get_path_to_bin(self, exe_name):
        """
        Computes the path to the pip executable, according to the OS
        """
        if os.name == 'nt':
            return os.path.join(self.path, "Scripts", exe_name + ".exe")

        return os.path.join(self.path, "bin", exe_name)

    def install_package(self, package):
        """Interface to `pip install SINGLE_PACKAGE`"""
        cmd = [self._get_path_to_bin('pip'), "install", package]

        if self._pypi_index_url is not None:
            cmd += ["-i", self._pypi_index_url]

        if self._use_wheel:
            cmd += ['--use-wheel']

        _exec_shell_cmd(
            cmd, stdout=self._out_stream, stderr=self._err_stream,
            err_msg="Failed to install {0} package."
            " Run with --verbose for detailed info.".format(package))

    def install_from_requirements(self, req):
        """Interface to `pip install -r REQUIREMENTS_FILE`"""
        cmd = [self._get_path_to_bin('pip'), "install", "-r", req]

        if self._pypi_index_url is not None:
            cmd += ["-i", self._pypi_index_url]

        if self._use_wheel:
            cmd += ['--use-wheel']

        _exec_shell_cmd(
            cmd, stdout=self._out_stream, stderr=self._err_stream,
            err_msg="Failed to install dependencies for this topology."
            " Run with --verbose for detailed info.")

    def execute_module(self, module, args=None, cwd=None):
        """Call "virtualenv/interpreter -m" to execute a python module."""
        cmd = [self._get_path_to_bin("python"), "-m", module]

        if args:
            cmd += args

        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                cwd=cwd)
        out_data, err_data = proc.communicate()
        if proc.returncode != 0:
            raise VirtualenvError("Failed to execute Python module: {0}."
                                  " Error: {1}".format(module, err_data))
        return to_str(out_data)
