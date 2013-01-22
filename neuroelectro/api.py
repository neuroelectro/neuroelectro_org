from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from neuroelectro.models import Article,Neuron,EphysProp,NeuronEphysDataMap,NeuronConceptMap,EphysConceptMap,NeuronEphysSummary,DataSource,DataTable
from django.conf.urls.defaults import url

class ArticleResource(ModelResource):
    class Meta:
        queryset = Article.objects.all()
        resource_name = 'a'
        include_resource_uri = False
        filtering = {
            'pmid' : ALL,
            }
    #def override_urls(self):
    #    return [
    #        url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
    #        url(r"^(?P<resource_name>%s)/(?P<pmid>\d+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
    #    ]

class DataTableResource(ModelResource):
    a = fields.ForeignKey(ArticleResource,'article',full=False)
    class Meta:
        queryset = DataTable.objects.all()
        resource_name = 'table'
        excludes = ['table_text','table_html','date_mod','needs_expert','id',]#,'article__abstract']
        include_resource_uri = False
        filtering = {
            'a' : ALL_WITH_RELATIONS,
            }

class DataSourceResource(ModelResource):
    table = fields.ForeignKey(DataTableResource,'data_table',full=True)
    class Meta:
        queryset = DataSource.objects.all()
        resource_name = 'source'
        excludes = ['id',]
        include_resource_uri = False
        filtering = {
            'table' : ALL_WITH_RELATIONS,
            }

class NeuronResource(ModelResource):
    #neuronephyssummary = fields.ToManyField('neuroelectro.api.NeuronEphysSummaryResource', 'neuronephyssummary_set', full=True)
    class Meta:
        queryset = Neuron.objects.all()
        resource_name = 'n'
        include_resource_uri = False
        excludes = ['added_by', 'added_by_old', 'date_mod']
        filtering = {
            'id' : ALL,
            'nlex_id' : ALL,
            }
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<nlex_id>\w+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

class EphysPropResource(ModelResource):
    class Meta:
        queryset = EphysProp.objects.all()
        resource_name = 'e'
        #excludes = ['definition']
        include_resource_uri = False
        filtering = {
            'id' : ALL,
            'name' : ALL,
            }
    
class NeuronConceptMapResource(ModelResource):
    n = fields.ForeignKey(NeuronResource,'neuron',full=True)
    source = fields.ForeignKey(DataSourceResource,'source')
    class Meta:
        queryset = NeuronConceptMap.objects.all()
        resource_name = 'ncm'    
        include_resource_uri = False
        excludes = ['added_by','added_by_old','date_mod','dt_id','id','match_quality']
        filtering = {
            'n' : ALL_WITH_RELATIONS,
            'source' : ALL_WITH_RELATIONS,
            }

class EphysConceptMapResource(ModelResource):
    e = fields.ForeignKey(EphysPropResource,'ephys_prop',full=True)
    source = fields.ForeignKey(DataSourceResource,'source')
    class Meta:
        queryset = EphysConceptMap.objects.all()
        resource_name = 'ecm'    
        include_resource_uri = False
        excludes = ['added_by','added_by_old','date_mod','dt_id','id','match_quality']
        filtering = {
            'e' : ALL_WITH_RELATIONS,
            'source' : ALL_WITH_RELATIONS,
            }
    # Remove ephys_prop definition from fields returned.  
    def dehydrate(self, bundle):
        bundle.data['e'].data.pop('definition')
        return bundle
        
class NeuronEphysDataMapResource(ModelResource):
    ncm = fields.ForeignKey(NeuronConceptMapResource, 'neuron_concept_map', full=True)
    ecm = fields.ForeignKey(EphysConceptMapResource, 'ephys_concept_map', full=True)
    source = fields.ForeignKey(DataSourceResource, 'source', full=True)
    class Meta:
        queryset = NeuronEphysDataMap.objects.all()
        resource_name = 'nedm'
        excludes = ['added_by','added_by_old','date_mod','dt_id','ref_text','id','match_quality','val_norm']
        include_resource_uri = False
        filtering = {
            'ncm' : ALL_WITH_RELATIONS,
            'ecm' : ALL_WITH_RELATIONS,
            'source' : ALL_WITH_RELATIONS,
            }
    # Allow filtering by fields deeper than ncm, e.g. the ncm__neuron, using identifiers like nlex_id.  
    def dispatch(self, request_type, request, **kwargs):
        # For some retarded reason 'n' is reserved in a very specific case so I have to purge it from the request dictionary.  
        if 'n' in request.GET:
            request.GET = request.GET.copy()
            request.GET['n1'] = request.GET['n']
            del request.GET['n']

        keys = ['n1','neuron']
        for key in keys:
            if key in request.GET:
                kwargs['ncm__n'] = Neuron.objects.get(id=request.GET[key])
                #del request.GET[key]
                #request.GET['ncm__n'] = str(Neuron.objects.get(id=neuron_id).id)
                break

        keys = ['neuron__nlex_id','neuron__nlex','nlex']
        for key in keys:
            if key in request.GET:
                kwargs['ncm__n'] = Neuron.objects.get(nlex_id=request.GET[key])
                break

        keys = ['e','ephys_prop','ephys_prop_id']
        for key in keys:
            if key in request.GET:
                kwargs['ecm__e'] = EphysProp.objects.get(id=request.GET[key])
                break

        keys = ['pmid']
        for key in keys:
            if key in request.GET:
                kwargs['source__table__a'] = Article.objects.get(pmid=request.GET[key])
                break

        #print request.GET
        #print kwargs
        return super(NeuronEphysDataMapResource, self).dispatch(request_type, request, **kwargs)

class NeuronEphysSummaryResource(ModelResource):
    e = fields.ForeignKey(EphysPropResource, 'ephys_prop', full=True)
    n = fields.ForeignKey(NeuronResource, 'neuron', full=True)
    class Meta:
        queryset = NeuronEphysSummary.objects.all()
        resource_name = 'nes'
        include_resource_uri = False
        excludes = ['id', 'data', 'date_mod']
        filtering = {
            'n' : ALL_WITH_RELATIONS,
            'e' : ALL_WITH_RELATIONS,
            }
    # Allow filtering by fields deeper than ncm, e.g. the ncm__neuron, using identifiers like nlex_id.  
    def dispatch(self, request_type, request, **kwargs):
        # For some retarded reason 'n' is reserved in a very specific case so I have to purge it from the request dictionary.  
        '''if 'n' in request.GET:
            request.GET = request.GET.copy()
            request.GET['n1'] = request.GET['n']
            del request.GET['n']
        '''
        keys = ['n1','neuron']
        for key in keys:
            if key in request.GET:
                kwargs['n'] = Neuron.objects.get(id=request.GET[key])

        keys = ['neuron__nlex_id','neuron__nlex','nlex']
        for key in keys:
            if key in request.GET:
                kwargs['n'] = Neuron.objects.get(nlex_id=request.GET[key])
        
        keys = ['e','ephys_prop','ephys_prop_id']
        for key in keys:
            if key in request.GET:
                kwargs['e'] = EphysProp.objects.get(id=request.GET[key])
        
        return super(NeuronEphysSummaryResource, self).dispatch(request_type, request, **kwargs)


