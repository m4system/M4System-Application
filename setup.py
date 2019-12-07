from setuptools import setup

setup(
    name='m4system',
    version='0.5',
    packages=['bin', 'webview', 'webview.migrations', 'scheduler', 'scheduler.management',
              'scheduler.management.commands', 'scheduler.migrations'],
    url='https://m4system.com',
    license='GPL v3',
    author='Daniel Gagnon',
    author_email='moi@danielgagnon.info',
    description='M is for Modern Monitoring and Management'
)
