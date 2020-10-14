from setuptools import setup

setup(name='tle2czml',
      version='0.2',
      description='Convert TLE\'s to CZML file',
      url='https://github.com/kujosHeist/tle2czml',
      author='Shane Carty',
      author_email='shane.carty@hotmail.com',
      license='MIT',
      packages=['tle2czml'],
      install_requires=[
      	'pygeoif==0.7',
		'python-dateutil==2.6.1',
		'pytz==2018.3',
		'sgp4==1.4',
		'six==1.11.0',
		'wheel==0.24.0',      	
      ],
      include_package_data=True,
      zip_safe=False)








