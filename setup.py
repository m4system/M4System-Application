import os

from setuptools import setup, find_packages


def strip_comments(l):
    return l.split('#', 1)[0].strip()


def _pip_requirement(req):
    if req.startswith('-r '):
        _, path = req.split()
        return reqs(*path.split('/'))
    return [req]


def _reqs(*f):
    return [
        _pip_requirement(r) for r in (
            strip_comments(l) for l in open(
            os.path.join(os.getcwd(), *f)).readlines()
        ) if r]


def reqs(*f):
    return [req for subreq in _reqs(*f) for req in subreq]


setup(
    name='M4',
    version='1.1',
    # packages=['M4', 'System', 'System.models', 'System.migrations', 'SNMPSourcePlugin', 'SNMPSourcePlugin.migrations',
    #           'ModbusSourcePlugin', 'ModbusSourcePlugin.migrations', 'EmailAlertHookPlugin',
    #           'EmailAlertHookPlugin.migrations', 'DashboardDisplayPlugin', 'DashboardDisplayPlugin.migrations',
    #           'ThresholdTriggerPlugin', 'ThresholdTriggerPlugin.migrations'],
    packages=find_packages(),
    url='https://m4system.com',
    license='AGPL3',
    author='Daniel Gagnon',
    author_email='moi@danielgagnon.info',
    description='M is for Modern Monitoring and Management',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License:: OSI Approved :: BSD License',
        'Environment :: No Input/Output (Daemon)',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Manufacturing',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Natural Language :: French',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: JavaScript',
        'Topic :: Home Automation',
        'Topic :: System :: Networking'
    ],
    install_requires=reqs('requirements.txt'),
    # scripts=[os.path.join('M4', 'manage.py')],
    # entry_points={'console_scripts': ['manage=M4.manage:main']},
)
