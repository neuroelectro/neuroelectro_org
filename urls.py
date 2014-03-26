from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from tastypie.api import Api
from neuroelectro.models import DataTable, Article, ArticleFullText
import neuroelectro.api
import inspect



# Override tastypie.serializers.Serializer.to_html so that 'format=json' is not needed.  
# json will be the new default, and a request for html will be passed to the json serializer.  
# Remove if/when tastypie implements the to_html serializer.   
from tastypie.serializers import Serializer
def to_html(self, data, options=None):
    return Serializer.to_json(self, data, options=options) # RICK EDIT
Serializer.to_html = to_html

# Register the admin interface.  
admin.autodiscover()


# Add every resource class (except the base resource class) in neuroelectro.api to the API.  
v1_api = Api(api_name='1')
for (class_name,class_object) in inspect.getmembers(neuroelectro.api):
    if 'Resource' in class_name and class_name != 'ModelResource':
    	v1_api.register(class_object())

urlpatterns = patterns("",
    url('^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
    url(r'^neuroelectro/', include('neuroelectro.urls'),name='neuroelectro'),
    url(r'^', include('neuroelectro.urls'),name='root'),
)

#urlpatterns += patterns('django.contrib.auth.views',
#	(r'^login$', 'login', {'template_name': 'neuroelectro/login.html',}),
#)

# For when there is no neuroelectro prefix in the url.  
urlpatterns += patterns('',
    url(r'', include('social_auth.urls')),
)