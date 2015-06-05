#!/bin/bash
# This script downloads and installs most of the prerequisites for the NeuroElectro project (Unix version)
# It requires:
# 1) Stable internet connection
# 2) Clone the latest version of the project from https://github.com/neuroelectro/neuroelectro_org
# 3) Python 2.7 or later must be already installed on the system and be accessible via $PATH (i.e. python --version call should work from within the Neuroelectro folder)
# 4) Navigate to neuroelectro_org folder and run the Neuroelectro_setup_exports.sh 
# 5) Obtain local_settings.py file from Dmitry or Shreejoy
# 6) Navigate to neuroelectro_org folder and execute this script with root permissions

pip install django==1.6.5 # Or https://www.djangoproject.com/download/1.6.5/tarball/ - extract and run setup.py install
pip install django-extensions
pip install django-contrib-comments
pip install urllib3 # If this is not enough - go into python2.7/site-packages/social/utils.py and edit the line 13 by removing "requests.packages" (before urllib3)
pip install django-crispy-forms
pip install django-tastypie
pip install south
pip install django-blog-zinnia
pip install django-localflavor-us
pip install django-picklefield
apt-get install libmysqlclient-dev
-E pip install mysql-python

mysqlDir=$(dirname $(dirname $(which mysql)))
cp "$mysqlDir/lib/libmysqlclient.18.dylib" ${PWD}

pip install pillow
pip install nltk
pip install django-mptt
pip install django-ckeditor-updated
pip install django-social-auth
pip install python-social-auth