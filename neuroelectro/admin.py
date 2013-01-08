from models import Article, Journal
from models import Neuron, Protein, BrainRegion
from models import DataTable
from models import EphysProp
from django.contrib import admin

admin.site.register(Article)
admin.site.register(Journal)
admin.site.register(Neuron)
admin.site.register(BrainRegion)
admin.site.register(Protein)
admin.site.register(DataTable)
admin.site.register(EphysProp)
