''' script to be used by setuptools to build package '''
import setuptools

with open("README.md", "r") as file:
    LONG_DESCRIPTION = file.read()

setuptools.setup(
    name='tle2czml',
    version='0.3',
    author='Shane Carty',
    author_email='shane.carty87@gmail.com',
    description='Convert TLE\'s to CZML file',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/kujosHeist/tle2czml',
    packages=['tle2czml'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pygeoif>=0.7',
        'python-dateutil>=2.6.1',
        'pytz>=2018.3',
        'sgp4>=1.4',
        'six>=1.11.0',
        'wheel>=0.24.0',
    ],
    include_package_data=True,
    zip_safe=False
)
