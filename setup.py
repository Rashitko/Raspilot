from setuptools import setup

setup(
    name='raspilot',
    version='',
    packages=['raspilot', 'raspilot.utils', 'raspilot.runner', 'raspilot.modules',
              'raspilot.commands', 'raspilot.recorders', 'raspilot.ground_proxy', 'raspilot.flight_controller',
              'raspilot._flight_controller'],
    url='',
    license='',
    author='Michal Raška',
    author_email='michal.raska@gmail.com',
    description='',
    install_requires=['up', 'twisted', 'pyserial', 'psutil', 'pid'],
    scripts=['bin/raspilot-run', 'bin/raspilot-update', 'bin/raspilot-logs'],
)
