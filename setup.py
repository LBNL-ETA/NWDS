# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 13:08:15 2018

@author: benoi
"""

from setuptools import setup, find_packages
import os
import noaa_weather_data_scraper as nwds

setup(name = 'NOAA Weather Data Scraper',
      version = nwds.__version__,
      author = 'Benoit Chabot',
      author_email = 'benoit.chabot17@gmail.com',
      maintainer = 'Laboratoire national Lawrence-Berkeley',
      maintainer_email = '',
      keywords = 'python LBNL weather data NOAA',
      packages = ['noaa_weather_data_scraper'],
      description = 'BETA TEST WEATHER DATA TOOL NOAA',
      long_description = open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
      install_requires = ['numpy',
                          'pandas',
                          'datetime',
                          'requests',
                          'pytz',
                          'geocoder',
                          'argparse',
                          'matplotlib'],
      platforms = 'ALL',
     )