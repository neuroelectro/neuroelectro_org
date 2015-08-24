![NeuroElectro Logo](https://raw.githubusercontent.com/neuroelectro/neuroelectro_org/master/media/images/neuroelectro.png)
![Travis CI status](https://travis-ci.org/neuroelectro/neuroelectro_org.svg?branch=pypi)

For the main objectives of this project, see the README on the main branch.  

This branch reflects the Neuroelectro Python API.  You can install it with:  

`pip install neuroelectro`

You can then explore the data with: 

`manage_neuroelectro shell`

which will bring up the python shell for exploring the data.  From within the shell, the data can be queried using the Django ORM syntax, e.g.:

```
import neuroelectro.models as m
print("There are %d neurons here." % m.Neuron.objects.count())
print("Here is one random piece of information")
print(m.NeuronEphysDataMap.objects.all()[0].__dict__)
```

More to come including an IPython notebook that uses the API to do some analysis of the data.  

