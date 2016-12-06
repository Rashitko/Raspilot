from distutils.core import setup

setup(
    name='raspilot',
    version='',
    packages=['raspilot', 'raspilot.utils', 'raspilot.config', 'raspilot.runner', 'raspilot.modules',
              'raspilot.commands', 'raspilot.recorders', 'raspilot.ground_proxy', 'raspilot.flight_controller',
              'raspilot._flight_controller'],
    url='',
    license='',
    author='Michal Raška',
    author_email='michal.raska@gmail.com',
    description='',
    requires=['up', 'twisted', 'pyserial'],
    scripts=['bin/raspilot-run', 'bin/raspilot-update']
)
