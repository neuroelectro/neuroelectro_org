# From: http://stackoverflow.com/questions/2720014/upgrading-all-packages-with-pip
# this script updates all installed python packages, run with sudo on a Mac OS X
import pip
from subprocess import call

for dist in pip.get_installed_distributions():
    call("pip install --upgrade " + dist.project_name, shell=True)