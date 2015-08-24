![NeuroElectro Logo](https://raw.githubusercontent.com/neuroelectro/neuroelectro_org/master/media/images/neuroelectro.png)
![Travis CI status](https://travis-ci.org/neuroelectro/neuroelectro_org.svg?branch=pypi)

For the main objectives of this project, see the README on the main branch.  

This branch reflects the Neuroelectro Python API.  You can install it with:  

`pip install neuroelectro`

You should then download and synchronize the database with:

`manage_neuroelectro sync`

after which you can explore the data with: 

`manage_neuroelectro shell`

which will bring up a python shell for exploring the data.  From within the shell, the data can be queried using the Django ORM syntax, e.g.:

```
import neuroelectro.models as m
print("There are %d neurons here." % m.Neuron.objects.count())
print("Here is one random piece of information")
print(m.NeuronEphysDataMap.objects.all()[0].__dict__)
```

If you want to interact with the data in a script you'll need to first run:  

```
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "neuroelectro.settings")
```

before making the Django ORM calls.  

More to come including an IPython notebook that uses the API to do some analysis of the data.  

