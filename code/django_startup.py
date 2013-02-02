# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 15:03:07 2011

@author: Shreejoy
"""
import os
from django.core.management import setup_environ

os.chdir('C:\Users\Shreejoy\Desktop\Neuroelectro_org')

import settings

setup_environ(settings)
#os.chdir('C:\Users\Shreejoy\Desktop\neuroelectro_org')
#from neuroelectro.models import *
#os.chdir('C:\Users\Shreejoy\Desktop\Biophysiome')