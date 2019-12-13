import os

from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


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
    packages=find_packages(),
    include_package_data=True,
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
    scripts=[os.path.join('M4', 'manage.py')],
    entry_points={'console_scripts': ['manage=M4.manage:main']},
)
