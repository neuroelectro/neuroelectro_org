from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from neuroelectro.models import Article,Neuron,EphysProp,NeuronEphysDataMap,NeuronConceptMap,NeuronEphysSummary,DataSource,DataTable
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
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<pmid>\d+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

class NeuronResource(ModelResource):
    #neuronephyssummary = fields.ToManyField('neuroelectro.api.NeuronEphysSummaryResource', 'neuronephyssummary_set', full=True)
    class Meta:
        queryset = Neuron.objects.all()
        resource_name = 'n'
        include_resource_uri = False
        excludes = ['added_by', 'added_by_old', 'date_mod']
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
        #excludes = ['definition']
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
        excludes = ['added_by','added_by_old','date_mod','dt_id','id','match_quality']
        filtering = {
            'neuron' : ALL_WITH_RELATIONS,
            'datasource' : ALL_WITH_RELATIONS,
            }

class EphysConceptMapResource(ModelResource):
    ephys_prop = fields.ForeignKey(EphysPropResource,'ephys_prop',full=True)
    class Meta:
        queryset = NeuronConceptMap.objects.all()
        resource_name = 'ecm'    
        include_resource_uri = False
        excludes = ['added_by','added_by_old','date_mod','dt_id','id','match_quality']
        filtering = {
            'ephys_prop' : ALL_WITH_RELATIONS,
            'datasource' : ALL_WITH_RELATIONS,
            }
    # Remove ephys_prop definition from fields returned.  
    def dehydrate(self, bundle):
        bundle.data['ephys_prop'].data.pop('definition')
        return bundle

class DataTableResource(ModelResource):
    article = fields.ForeignKey(ArticleResource,'article',full=False)
    class Meta:
        queryset = DataTable.objects.all()
        resource_name = 'table'
        excludes = ['table_text','table_html','date_mod','needs_expert','id',]#,'article__abstract']
        include_resource_uri = False
        filtering = {
            'article' : ALL_WITH_RELATIONS,
            }

class DataSourceResource(ModelResource):
    data_table = fields.ForeignKey(DataTableResource,'data_table',full=True)
    class Meta:
        queryset = DataSource.objects.all()
        resource_name = 'source'
        excludes = ['id',]
        include_resource_uri = False
        filtering = {
            'data_table' : ALL_WITH_RELATIONS,
            }
        
class NeuronEphysDataMapResource(ModelResource):
    ncm = fields.ForeignKey(NeuronConceptMapResource, 'neuron_concept_map', full=True)
    epcm = fields.ForeignKey(EphysConceptMapResource, 'ephys_concept_map', full=True)
    source = fields.ForeignKey(DataSourceResource, 'source', full=True)
    class Meta:
        queryset = NeuronEphysDataMap.objects.all()
        resource_name = 'nedm'
        excludes = ['added_by','added_by_old','date_mod','dt_id','ref_text','id','match_quality','val_norm']
        include_resource_uri = False
        filtering = {
            'ncm' : ALL_WITH_RELATIONS,
            'epcm' : ALL_WITH_RELATIONS,
            'source' : ALL_WITH_RELATIONS,
            }
    # Allow filtering by fields deeper than ncm, e.g. the ncm__neuron, using identifiers like nlex_id.  
    def dispatch(self, request_type, request, **kwargs):
        nlex_id = None
        keys = ['neuron__nlex_id','neuron__nlex','nlex']
        for key in keys:
            if key in request.GET:
                nlex_id = request.GET[key]
                kwargs['ncm__neuron'] = Neuron.objects.get(nlex_id=nlex_id)
                break

        ephys_prop_id = None
        keys = ['ephys_prop','ephys_prop_id']
        for key in keys:
            if key in request.GET:
                ephys_prop_id = request.GET[key]    
                kwargs['epcm__ephys_prop'] = EphysProp.objects.get(id=ephys_prop_id)
                break

        pmid = None
        keys = ['pmid']
        for key in keys:
            if key in request.GET:
                pmid = request.GET[key]
                kwargs['source__data_table__article'] = Article.objects.get(pmid=pmid)
                break

        return super(NeuronEphysDataMapResource, self).dispatch(request_type, request, **kwargs)

class NeuronEphysSummaryResource(ModelResource):
    ephys_prop = fields.ForeignKey(EphysPropResource, 'ephys_prop', full=True)
    neuron = fields.ForeignKey(NeuronResource, 'neuron', full=True)
    class Meta:
        queryset = NeuronEphysSummary.objects.all()
        resource_name = 'nes'
        include_resource_uri = False
        excludes = ['id', 'data', 'date_mod']
        filtering = {
            'neuron' : ALL_WITH_RELATIONS,
            'ephys_prop' : ALL_WITH_RELATIONS,
            }
    # Allow filtering by fields deeper than ncm, e.g. the ncm__neuron, using identifiers like nlex_id.  
    def dispatch(self, request_type, request, **kwargs):
        nlex_id = None
        keys = ['neuron__nlex_id','neuron__nlex','nlex']
        for key in keys:
            if key in request.GET:
                nlex_id = request.GET[key]
        if nlex_id:
            kwargs['neuron'] = Neuron.objects.get(nlex_id=nlex_id)
        
        ephys_prop_id = None
        keys = ['ephys_prop','ephys_prop_id']
        for key in keys:
            if key in request.GET:
                ephys_prop_id = request.GET[key]    
        if ephys_prop_id:
            kwargs['ephys_prop'] = EphysProp.objects.get(id=ephys_prop_id)
        return super(NeuronEphysSummaryResource, self).dispatch(request_type, request, **kwargs)


