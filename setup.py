from setuptools import setup, find_packages

setup(
    name='hhub',
    version="0.1",
    description="Home automation hub",
    author="Andrew Thigpen",
    packages=find_packages(),
    include_package_data=True,
    entry_points = {
        'console_scripts': [
            'hhub = hhub.client:client',
            'hhubd = hhub.hhub:daemon',
        ],
    },
)

