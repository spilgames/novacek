from setuptools import setup, find_packages
import sys


name = "novacek"
with open('CHANGELOG.md') as f:
    version = f.readline().strip().replace('%s-' % name, '')
requirements = [x.strip() for x in open('requirements.txt').readlines()]
description = open('README.md').read()

python_version = sys.version_info
if python_version[0] == 2 and python_version[1] <= 6:
    # Argparse is not included in python versions lower than 2.7
    requirements.insert(0, 'argparse>=1.2.1')

print requirements

setup(
    name=name,
    version=version,
    author="Robert van Leeuwen, Spil Games",
    author_email="robert.vanleeuwen@spilgames.com",
    description="Toolset for OpenStack hypervisor/instance information",
    long_description=description,
    url="https://github.com/spilgames/novacek",
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    entry_points = {
        'console_scripts': [
            'novacek = novacek.novacek:main',
            'test_hypervisor = novacek.test_hypervisor:main',
        ],
    }
)

