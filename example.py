import neuroelectro.models as m
assert m.Neuron.objects.count() > 50
print(m.Neuron.objects.all()[0].__dict__)
