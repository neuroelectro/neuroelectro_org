#!/bin/bash
# This script downloads and installs most of the prerequisites for the NeuroElectro project (Unix version)
# It requires:
# 1) Stable internet connection
# 2) Clone the latest version of the project from https://github.com/neuroelectro/neuroelectro_org
# 3) Python 2.7 or later must be already installed on the system and be accessible via $PATH (i.e. python --version call should work from within the Neuroelectro folder)
# 4) Navigate to neuroelectro_org folder and run the Neuroelectro_setup_exports.sh 
# 5) Obtain local_settings.py file from Dmitry or Shreejoy
# 6) Navigate to neuroelectro_org folder and execute this script with root permissions
# 7) If you want to query pubmed: download and install http://dev.mysql.com/downloads/connector/python/

sudo pip install django==1.8 # Or https://www.djangoproject.com/download/1.6.5/tarball/ - extract and run setup.py install
sudo pip install django-extensions
sudo pip install django-contrib-comments
sudo pip install urllib3 # If this is not enough - go into python2.7/site-packages/social/utils.py and edit the line 13 by removing "requests.packages" (before urllib3)
sudo pip install django-crispy-forms
sudo pip install django-tastypie==0.12.2
# If error: Cannot import module actions: go to django/contrib/admin/sites.py and delete "from django.contrib.admin import actions" and add "from django.contrib.admin.actions import delete_selected"
# Also same file: line 50 remove "actions" from the line
#sudo sudo pip install django-blog-zinnia==0.14.1
sudo pip install django-tagging==0.4 
sudo pip install django-mptt # downgrading for zinnia
sudo pip install django-localflavor-us
sudo pip install django-picklefield
apt-get install libmysqlclient-dev
sudo pip install mysql-python
#If error: try apt-get install python-mysqldb (ubuntu thing)
# On ubuntu/debian: apt-get install python-dev

#mysqlDir=$(dirname $(dirname $(which mysql)))
#cp "$mysqlDir/lib/libmysqlclient.18.dylib" ${PWD}

# Import sql dump file


sudo pip install numpy
sudo pip install pillow
sudo pip install fuzzywuzzy
sudo pip install nltk
sudo pip install django-ckeditor-updated
sudo pip install python-social-auth
#sudo pip uninstall south 
# If error - you may have to uninstall south
sudo pip install pylab
sudo pip install simplejson
sudo pip install django-simple-history
sudo pip install django-fixture-magic
sudo pip install Pint # for sci unit conversion magic
sudo pip install sqlparse
sudo pip install pandas

sudo pip install sqlalchemy
sudo pip install regex
sudo pip install selenium

# import ACE repo from neuroelectro github
git clone -b sectionparser https://github.com/neuroelectro/ACE.git
cd ACE
python setup.py install
cd ..

# install allensdk for atlas structure ontology stuff
sudo pip install https://github.com/AllenInstitute/AllenSDK/archive/v0.10.1.tar.gz --no-deps
sudo pip install pynrrd
sudo pip install jinja2

sudo pip install django-extensions
sudo pip install bs4
sudo pip install python-levenshtein
sudo pip install xlrd
sudo pip install lxml




