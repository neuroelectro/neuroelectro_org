from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from neuroelectro.models import Article,Neuron,EphysProp,NeuronEphysDataMap,NeuronConceptMap,NeuronEphysSummary
from django.conf.urls.defaults import url

class ArticleResource(ModelResource):
    class Meta:
        queryset = Article.objects.all()
        resource_name = 'a'
        include_resource_uri = False
        filtering = {
            'pmid' : ALL,
            }
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/pk(?P<pk>\d+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<pmid>\d+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

class NeuronResource(ModelResource):
    #neuronephyssummary = fields.ToManyField('neuroelectro.api.NeuronEphysSummaryResource', 'neuronephyssummary_set', full=True)
    class Meta:
        queryset = Neuron.objects.all()
        resource_name = 'n'
        include_resource_uri = False
        excludes = ['added_by', 'date_mod','id']
        filtering = {
        	'nlex_id' : ALL,
            }
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/pk(?P<pk>\d+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<nlex_id>\w+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]


class EphysPropResource(ModelResource):
    class Meta:
        queryset = EphysProp.objects.all()
        resource_name = 'e'
        excludes = ['definition']
        include_resource_uri = False
        filtering = {
        	'name' : ALL,
        	'id' : ALL,
            }

class NeuronConceptMapResource(ModelResource):
    neuron = fields.ForeignKey(NeuronResource,'neuron',full=True)
    class Meta:
        queryset = NeuronConceptMap.objects.all()
        resource_name = 'ncm'    
        include_resource_uri = False
        excludes = ['added_by','date_mod','dt_id','id','match_quality']
        filtering = {
            'neuron' : ALL_WITH_RELATIONS,
            'datasource' : ALL_WITH_RELATIONS,
            }

class EphysConceptMapResource(ModelResource):
    neuron = fields.ForeignKey(NeuronResource,'neuron',full=True)
    class Meta:
        queryset = NeuronConceptMap.objects.all()
        resource_name = 'ecm'    
        include_resource_uri = False
        excludes = ['added_by','date_mod','dt_id','id','match_quality']
        filtering = {
            'ephysprop' : ALL_WITH_RELATIONS,
            'datasource' : ALL_WITH_RELATIONS,
            }

class NeuronEphysDataMapResource(ModelResource):
    ncm = fields.ForeignKey(NeuronConceptMapResource, 'neuron_concept_map', full=True)
    class Meta:
        queryset = NeuronEphysDataMap.objects.all()
        resource_name = 'nedm'
        excludes = ['added_by','date_mod','dt_id','ref_text','id','match_quality','val_norm']
        include_resource_uri = False
        filtering = {
            'ncm' : ALL_WITH_RELATIONS,
            'epcm' : ALL_WITH_RELATIONS,
            }
    # Allow filtering by fields deeper than ncm, e.g. the ncm__neuron, using identifiers like nlex_id.  
    def dispatch(self, request_type, request, **kwargs):
        nlex_id = None
        if 'neuron__nlex_id' in request.GET:
            nlex_id = request.GET['neuron__nlex_id']
        if 'nlex' in request.GET:
            nlex_id = request.GET['nlex']
        if nlex_id:
            kwargs['ncm__neuron'] = Neuron.objects.get(nlex_id=nlex_id)
        return super(NeuronEphysDataMapResource, self).dispatch(request_type, request, **kwargs)

class NeuronEphysSummaryResource(ModelResource):
	ephysprop = fields.ForeignKey(EphysPropResource, 'ephys_prop', full=True)
	neuron = fields.ForeignKey(NeuronResource, 'neuron', full=True)
	class Meta:
		queryset = NeuronEphysSummary.objects.all()
		resource_name = 'nes'
		include_resource_uri = False
		excludes = ['id', 'data', 'date_mod']
		filtering = {
			'neuron' : ALL_WITH_RELATIONS,
			'ephysprop' : ALL_WITH_RELATIONS,
            }


