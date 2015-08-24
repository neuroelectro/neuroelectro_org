from setuptools import setup
from setuptools.command.install import install
from subprocess import call

class Bootstrap(install):
    def run(self):
        install.run(self)
        call(["manage_neuroelectro syncdb --noinput"], shell=True)
        call(["curl -L -o ~/.neuroelectro/data.json https://www.dropbox.com/s/58d85a2b24n3tf3/validated_data.json?dl=0"], shell=True)
        call(["manage_neuroelectro loaddata ~/.neuroelectro/data.json"], shell=True)

setup(
	name='neuroelectro',
	version='0.0.1',
	author='Rick Gerkin',
	author_email='rgerkin@asu.edu',
        packages=[
            'neuroelectro',
            'neuroelectro.db_functions',
            ],
        url='http://github.com/neuroelectro/neuroelectro',
	license='GPL2',
        description='Electrophysiological information from diverse neuron types',
        long_description="The aim of the NeuroElectro Project is to represent structured electrophysiological information from diverse neuron types",
        setup_requires=['django-simple-history'],
        install_requires=['django_localflavor_us','django-picklefield','django-simple-history'],
        entry_points = {
            'console_scripts': [
                'manage_neuroelectro = neuroelectro.manage:main',
                ],
            },
        cmdclass={
            'install': Bootstrap,
        },
    )
