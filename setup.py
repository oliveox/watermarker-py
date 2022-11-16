from setuptools import setup, find_packages
from distutils import cmd, log
import subprocess

class FormatCommand(cmd.Command):
    """A custom command to run Pylint on all Python source files."""

    description = 'run black on Python source files'
    user_options = [
    ]

    def initialize_options(self):
        """Set default values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
        pass

    def run(self):
        """Run command."""
        command = ['black', 'src', 'tests']
        self.announce(
            'Running command: %s' % str(command),
            level=log.INFO)
        subprocess.check_call(command)

class LintCommand(cmd.Command):
    """A custom command to run Pylint on all Python source files."""

    description = 'run flake8 on Python source files'
    user_options = [
    ]

    def initialize_options(self):
        """Set default values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
        pass

    def run(self):
        """Run command."""
        command = ['flake8', 'src', 'tests']
        self.announce(
            'Running command: %s' % str(command),
            level=log.INFO)
        subprocess.check_call(command)

class FixCommand(cmd.Command):
    """A custom command to run Pylint on all Python source files."""

    description = 'run all checks'
    user_options = [
    ]

    def initialize_options(self):
        """Set default values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
        pass

    def run(self):
        """Run command."""
        self.run_command('lint')
        self.run_command('format')

setup(
    name='watermarker',
    use_scm_version=True,
    packages=find_packages(),
    setup_requires=['setuptools_scm'],
    install_requires=[line.rstrip('\n') for line in open('requirements.txt')],
    include_package_data=True,
    zip_safe=False,
    cmdclass={
        'lint': LintCommand,
        'format': FormatCommand,
        'fix': FixCommand
    },
)
