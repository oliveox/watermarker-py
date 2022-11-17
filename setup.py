from setuptools import setup, find_packages

from src.setup_classes import MetricsCommand, FormatCommand, ImportFormatCommand, LintCommand, FixCommand, \
    TypeCheckCommand

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
        'format_imports': ImportFormatCommand,
        'type_check': TypeCheckCommand,
        'fix': FixCommand,
        'metrics': MetricsCommand,
    },
)
