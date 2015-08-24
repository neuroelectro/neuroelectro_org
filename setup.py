from setuptools import setup
from setuptools.command.install import install
from subprocess import call

requirements = ['Django','django-extensions','django-localflavor-us','django-picklefield','django-simple-history']

class Bootstrap(install):
    def run(self):
        for requirement in requirements:
            call(["pip install -U %s" % requirement], shell=True)
        call(["cp manage.py neuroelectro/manage.py"], shell=True)
        install.run(self)
        call(["manage_neuroelectro syncdb --noinput"], shell=True)
        call(["curl -L -o ~/.neuroelectro/data.json https://www.googledrive.com/host/0B2pE3nzQxTzBckFVSFRqN1VDY1k"], shell=True)
        call(["manage_neuroelectro loaddata ~/.neuroelectro/data.json"], shell=True)

setup(
	name='neuroelectro',
	version='0.0.2.1',
	author='Rick Gerkin',
	author_email='rgerkin@asu.edu',
        packages=[
            'neuroelectro',
            'neuroelectro.db_functions',
            ],
        url='http://github.com/neuroelectro/neuroelectro_org', # Use the pypi branch.  
	license='GPL2',
        description='Electrophysiological information from diverse neuron types',
        long_description="The aim of the NeuroElectro Project is to represent structured electrophysiological information from diverse neuron types",
        setup_requires=requirements,
        install_requires=requirements,
        entry_points = {
            'console_scripts': [
                'manage_neuroelectro = neuroelectro.manage:main',
                ],
            },
        cmdclass={
            'install': Bootstrap,
        },
    )
