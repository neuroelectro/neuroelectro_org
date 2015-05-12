#!/bin/bash
# This script downloads and installs most of the prerequisites for the Neuroelectro project (Mac version)
# It requires:
# 1) Stable internet connection
# 2) Pull the latest version of the project from https://bitbucket.org/rgerkin/neuroelectro_org
# 3) Python 2.7 or later must be already installed on the system and be accessible via $PATH (i.e. python --version call should work from within the Neuroelectro folder)
# 4) Navigate to neuroelectro_org folder and run the Neuroelectro_setup_exports.sh 
# 5) Navigate to neuroelectro_org folder and execute this script with root permissions

pip install django-extensions
pip install django-localflavor-us
pip install django-picklefield
-E pip install mysql-python

mysqlDir=$(dirname $(dirname $(which mysql)))
cp "$mysqlDir/lib/libmysqlclient.18.dylib" ${PWD}

pip install pillow
pip install nltk
pip install django-ckeditor-updated
