from models import Article, Journal
from models import Neuron
from models import DataTable
from models import EphysProp
from models import User, MailingListEntry, MetaData
from django.contrib import admin

admin.site.register(Article)
admin.site.register(Journal)
admin.site.register(MetaData)
admin.site.register(Neuron)
admin.site.register(DataTable)
admin.site.register(EphysProp)
admin.site.register(User)
admin.site.register(MailingListEntry)

