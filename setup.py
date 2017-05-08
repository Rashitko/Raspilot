from distutils.core import setup

setup(
    name='raspilot',
    version='0.5',
    packages=['modules', 'commands', 'flight_controller'],
    url='',
    license='',
    author='Michal Raska',
    author_email='michal.raska@gmail.com',
    description='Modular Autopilot for RC controlled Airplanes',
    install_requires=['up', 'termcolor'],
    scripts=['bin/raspilot-install']
)
