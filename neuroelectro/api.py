from datetime import datetime

from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
import neuroelectro.models as m
from django.conf.urls import url
from helpful_functions.dict_pop_multiple import dict_pop_multiple

class CustomModelResource(ModelResource):
    class Meta:
        pass
    def dispatch(self, request_type, request, **kwargs):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        entry = m.API(path=request.path,ip=ip)
        entry.save()
        return super(CustomModelResource, self).dispatch(request_type, request, **kwargs)

class ArticleResource(CustomModelResource):
    class Meta:
        queryset = m.get_articles_with_ephys_data()
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

class DataTableResource(CustomModelResource):
    a = fields.ForeignKey(ArticleResource,'article',full=False)
    class Meta:
        queryset = m.DataTable.objects.all()
        resource_name = 'table'
        excludes = ['table_text','table_html','date_mod','needs_expert','id',]#,'article__abstract']
        include_resource_uri = False
        filtering = {
            'a' : ALL_WITH_RELATIONS,
            }

class DataSourceResource(CustomModelResource):
    table = fields.ForeignKey(DataTableResource,'data_table',full=True)
    class Meta:
        queryset = m.DataSource.objects.all()
        resource_name = 'source'
        excludes = ['id',]
        include_resource_uri = False
        filtering = {
            'table' : ALL_WITH_RELATIONS,
            }

class NeuronResource(CustomModelResource):
    #neuronephyssummary = fields.ToManyField('neuroelectro.api.NeuronEphysSummaryResource', 'neuronephyssummary_set', full=True)
    class Meta:
        queryset = m.Neuron.objects.all()
        resource_name = 'n'
        include_resource_uri = False
        excludes = ['added_by', 'added_by_old', 'date_mod']
        filtering = {
            'id' : ALL,
            'name' : ALL,
            'nlex_id' : ALL,
            }
        limit = 300
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<nlex_id>\w+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

class EphysPropResource(CustomModelResource):
    class Meta:
        queryset = m.EphysProp.objects.all()
        resource_name = 'e'
        #excludes = ['definition']
        include_resource_uri = False
        filtering = {
            'id' : ALL,
            'name' : ALL,
            'nlex_id' : ALL,
            }
        limit = 50
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<nlex_id>\w+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]
    
class NeuronConceptMapResource(CustomModelResource):
    n = fields.ForeignKey(NeuronResource,'neuron',full=True)
    source = fields.ForeignKey(DataSourceResource,'source')
    class Meta:
        queryset = m.NeuronConceptMap.objects.all()
        resource_name = 'ncm'    
        include_resource_uri = False
        excludes = ['added_by','added_by_old','date_mod','dt_id','id','match_quality']
        filtering = {
            'n' : ALL_WITH_RELATIONS,
            'source' : ALL_WITH_RELATIONS,
            }

class EphysConceptMapResource(CustomModelResource):
    e = fields.ForeignKey(EphysPropResource,'ephys_prop',full=True)
    source = fields.ForeignKey(DataSourceResource,'source')
    class Meta:
        queryset = m.EphysConceptMap.objects.all()
        resource_name = 'ecm'    
        include_resource_uri = False
        excludes = ['added_by','added_by_old','date_mod','dt_id','id','match_quality']
        filtering = {
            'e' : ALL_WITH_RELATIONS,
            'source' : ALL_WITH_RELATIONS,
            }
    # Remove ephys_prop definition from fields returned.  
    def dehydrate(self, bundle):
        #tempbundle = dict_pop_multiple(bundle.data['e'].data, ['definition', 'norm_criteria'])
        #bundle.data['e'].data = dict_pop_multiple(bundle.data['e'].data, ['definition', 'norm_criteria'])
        bundle.data['e'].data = dict_pop_multiple(bundle.data['e'].data, ['definition', 'norm_criteria'])
        #bundle.data['e'].data.pop('definition')
        print bundle
        return bundle
        
class NeuronEphysDataMapResource(CustomModelResource):
    ncm = fields.ForeignKey(NeuronConceptMapResource, 'neuron_concept_map', full=True)
    ecm = fields.ForeignKey(EphysConceptMapResource, 'ephys_concept_map', full=True)
    source = fields.ForeignKey(DataSourceResource, 'source', full=True)
    class Meta:
        queryset = m.NeuronEphysDataMap.objects.filter(neuron_concept_map__times_validated__gte = 1)
        resource_name = 'nedm'
        excludes = ['added_by','added_by_old','date_mod','dt_id','ref_text','id','match_quality',]
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
                kwargs['ncm__n'] = m.Neuron.objects.get(id=request.GET[key])
                #del request.GET[key]
                #request.GET['ncm__n'] = str(Neuron.objects.get(id=neuron_id).id)
                break

        keys = ['neuron__nlex_id','neuron__nlex']
        for key in keys:
            if key in request.GET:
                kwargs['ncm__n'] = m.Neuron.objects.get(nlex_id=request.GET[key])
                break

        keys = ['e','ephys_prop','ephys_prop_id']
        for key in keys:
            if key in request.GET:
                kwargs['ecm__e'] = m.EphysProp.objects.get(id=request.GET[key])
                break

        keys = ['ephysprop__nlex_id','ephysprop__nlex']
        for key in keys:
            if key in request.GET:
                kwargs['ecm__e'] = m.EphysProp.objects.get(nlex_id=request.GET[key])
                break

        keys = ['nlex', 'nlex_id']
        for key in keys:
            if key in request.GET:
                e = m.EphysProp.objects.filter(nlex_id=request.GET[key])
                if e: 
                    kwargs['ecm__e'] = e[0]
                n = m.Neuron.objects.filter(nlex_id=request.GET[key])
                if n:
                    kwargs['ncm__n'] = n[0]
        
        keys = ['pmid']
        for key in keys:
            if key in request.GET:
                kwargs['source__table__a'] = m.Article.objects.get(pmid=request.GET[key])
                break

        #print request.GET
        #print kwargs
        return super(NeuronEphysDataMapResource, self).dispatch(request_type, request, **kwargs)

class NeuronEphysSummaryResource(CustomModelResource):
    e = fields.ForeignKey(EphysPropResource, 'ephys_prop', full=True)
    n = fields.ForeignKey(NeuronResource, 'neuron', full=True)
    class Meta:
        queryset = m.NeuronEphysSummary.objects.all()
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
                kwargs['n'] = m.Neuron.objects.get(id=request.GET[key])

        keys = ['neuron__nlex_id','neuron__nlex']
        for key in keys:
            if key in request.GET:
                kwargs['n'] = m.Neuron.objects.get(nlex_id=request.GET[key])
        
        keys = ['e','ephys_prop','ephys_prop_id']
        for key in keys:
            if key in request.GET:
                kwargs['e'] = m.EphysProp.objects.get(id=request.GET[key])

        keys = ['ephysprop__nlex_id','ephysprop__nlex']
        for key in keys:
            if key in request.GET:
                kwargs['e'] = m.EphysProp.objects.get(nlex_id=request.GET[key])

        keys = ['nlex', 'nlex_id']
        for key in keys:
            if key in request.GET:
                e = m.EphysProp.objects.filter(nlex_id=request.GET[key])
                if e: 
                    kwargs['e'] = e[0]
                n = m.Neuron.objects.filter(nlex_id=request.GET[key])
                if n:
                    kwargs['n'] = n[0]

        return super(NeuronEphysSummaryResource, self).dispatch(request_type, request, **kwargs)

class ContValueResource(CustomModelResource):
    class Meta:
        queryset = m.ContValue.objects.all()
        resource_name = 'cv'
        include_resource_uri = False

class MetaDataResource(CustomModelResource):
    cont_value = fields.ForeignKey(ContValueResource, 'cont_value', full=True, null=True)
    class Meta:
        queryset = m.MetaData.objects.all()
        resource_name = 'md'
        include_resource_uri = False
        filtering = {
            'cont_value' : ALL_WITH_RELATIONS,
            }

class ArticleMetaDataMapResource(CustomModelResource):
    a = fields.OneToOneField(ArticleResource, 'article', full=True)
    md = fields.OneToOneField(MetaDataResource,'metadata', full=True)
    class Meta:
        queryset = m.ArticleMetaDataMap.objects.filter(times_validated__gte = 1)
        resource_name = 'amdm'
        excludes = ['added_by','date_mod', 'note']
        include_resource_uri = False
        filtering = {
            'a' : ALL_WITH_RELATIONS,
            'md' : ALL_WITH_RELATIONS,
            }
        
    def dehydrate(self, bundle):
        bundle.data['a'].data = dict_pop_multiple(bundle.data['a'].data, ['abstract', 'author_list_str'])
        return bundle
    
    def dispatch(self, request_type, request, **kwargs):
        keys = ['a','article']
        for key in keys:
            if key in request.GET:
                kwargs['a'] = m.Article.objects.get(id=request.GET[key])
        
        keys = ['pmid']
        for key in keys:
            if key in request.GET:
                kwargs['a'] = m.Article.objects.get(pmid=request.GET[key])
                break
            
        return super(ArticleMetaDataMapResource, self).dispatch(request_type, request, **kwargs)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#     
#     
# 
# class ArticleMetaDataMapResource(CustomModelResource):
#     a = fields.ForeignKey(ArticleResource, 'article', full=True)
#     md = fields.ForeignKey(MetaDataResource, 'meta_data', full=True, null=True)
#     class Meta:
#         queryset = m.ArticleMetaDataMap.objects.all()
#         resource_name = 'amdm'
#         excludes = ['added_by','date_mod','times_validated', 'note']
#         include_resource_uri = False
#         filtering = {
#             'a' : ALL_WITH_RELATIONS,
#             'md' : ALL_WITH_RELATIONS,
#             }
#     def dehydrate(self, bundle):
#         bundle.data['a'].data.pop('abstract','author_list_str')
#         return bundle
#     def dispatch(self, request_type, request, **kwargs):
#         keys = ['a','article']
#         for key in keys:
#             if key in request.GET:
#                 kwargs['a'] = m.Article.objects.get(id=request.GET[key])
#         return super(ArticleMetaDataMapResource, self).dispatch(request_type, request, **kwargs)


