from distutils.command.bdist import bdist as _bdist
from distutils.core import Command
import os
import shutil
import subprocess
import sys

from setuptools import setup
from setuptools.command.sdist import sdist as _sdist

from pyleus import __version__
from pyleus import BASE_JAR

JAVA_SRC_DIR = "topology_builder"
BASE_JAR_SRC = os.path.join(JAVA_SRC_DIR, "dist", BASE_JAR)
BASE_JAR_DST = os.path.join("pyleus", BASE_JAR)


def which(cmd):
    try:
        # Available in Python 3.3+
        return shutil.which(cmd)
    except AttributeError:
        # Not implemented
        if os.name == 'win32':
            # File won't be found as is
            return None
        else:
            # Seems to work as is on POSIX systems
            return cmd


class build_java(Command):

    description = "Build the topology base JAR"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def _make_jar_make(self):
        make_path = which('make')
        if not make_path:
            raise IOError("make executable not found")

        subprocess.check_call([make_path, "-C", JAVA_SRC_DIR])

    def _make_jar_maven(self):
        pom_file = os.path.join(JAVA_SRC_DIR, 'pom.xml')

        # Try the "mvn" command (in path)
        mvn_path = which('mvn')
        if mvn_path:
            # Try the "mvn" command (in path)
            subprocess.check_call([mvn_path, '-f', pom_file, 'package'])
            return True

        # Try with the MAVEN_HOME path, if any
        maven_home = os.getenv("MAVEN_HOME")
        if not maven_home or not os.path.exists(maven_home):
            raise IOError("Maven executable not found")

        mvn_path = os.path.join(maven_home, 'bin', 'mvn')
        if os.name == 'nt':
            mvn_path += ".cmd"

        subprocess.check_call([mvn_path, '-f', pom_file, 'package'])

    def _make_jar(self):
        try:
            # Standard way, using make
            self._make_jar_make()
        except IOError:
            pass

        # Fall back on a direct call to Maven
        self._make_jar_maven()

    def _copy_jar(self):
        shutil.copy(BASE_JAR_SRC, BASE_JAR_DST)

    def run(self):
        self._make_jar()
        self._copy_jar()


try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
except ImportError:
    # No support of wheel
    bdist_wheel = None
else:
    class bdist_wheel(_bdist_wheel):

        sub_commands = [('build_java', None)]

        def run(self):
            for cmd_name in self.get_sub_commands():
                self.run_command(cmd_name)

            _bdist_wheel.run(self)


class bdist(_bdist):

    sub_commands = [('build_java', None)]

    def run(self):
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)

        _bdist.run(self)


class sdist(_sdist):

    sub_commands = [('build_java', None)]

    def run(self):
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)

        _sdist.run(self)


cmd_classes = {
    'build_java': build_java,
    'bdist': bdist,
    'sdist': sdist}

if bdist_wheel is not None:
    cmd_classes['bdist_wheel'] = bdist_wheel


def readme():
    with open("README.rst") as f:
        return f.read()


extra_install_requires = []
if sys.version_info < (2, 7):
    # argparse is in the standard library of Python >= 2.7
    extra_install_requires.append("argparse")


setup(
    name="pyleus",
    version=__version__,
    author="Patrick Lucas",
    author_email="plucas@yelp.com",
    description="Standard library and deployment tools for using Python "
        "with Storm",
    long_description=readme(),
    url="http://pyleus.org",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Distributed Computing",
        "Development Status :: 4 - Beta",
    ],
    packages=[
        "pyleus", "pyleus.cli", "pyleus.cli.commands",
        "pyleus.storm", "pyleus.storm.serializers"],
    entry_points={
        'console_scripts': [
            'pyleus = pyleus.cli.cli:main',
        ],
    },
    install_requires=[
        "PyYAML",
        "msgpack-python",
        "virtualenv",
        "six",
    ] + extra_install_requires,
    package_data={'pyleus': [BASE_JAR]},
    cmdclass=cmd_classes,
)
