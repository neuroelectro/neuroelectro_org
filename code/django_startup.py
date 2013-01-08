# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 15:03:07 2011

@author: Shreejoy
"""
import os
from django.core.management import setup_environ

#os.chdir('C:\Users\Shreejoy\Desktop\Biophysiome')

import settings

setup_environ(settings)
#os.chdir('C:\Python27\Scripts\Biophys\Biophysiome\neuroelectro')
#from neuroelectro.models import *
#os.chdir('C:\Users\Shreejoy\Desktop\Biophysiome')