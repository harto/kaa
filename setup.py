from setuptools import setup, find_packages

setup(name='kaa',
      version='0.0.0',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      entry_points={'console_scripts': ['kaa=kaa.main:main']})
