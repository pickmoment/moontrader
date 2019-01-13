
from setuptools import setup, find_packages
from moontrader.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='moontrader',
    version=VERSION,
    description='MyApp Does Amazing Things!',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Moongeun Kim',
    author_email='moongux@gmail.com',
    url='https://github.com/johndoe/myapp/',
    license='unlicensed',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'moontrader': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        moontrader = moontrader.main:main
    """,
)
