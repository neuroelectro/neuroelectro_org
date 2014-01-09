import os
from django.contrib import admin
from django import forms
import models as m
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.db.models import get_app,get_models
from django.contrib.admin.sites import AlreadyRegistered

def get_inlines(model):
    def get_inline(related_model):
        class GenericInline(admin.TabularInline):
            model = related_model
        return GenericInline
    meta = model._meta
    related_models = [x.model for x in model._meta.get_all_related_objects()]
    inlines = [get_inline(x) for x in related_models]
    return inlines
     
def get_admin(model):
    class GenericModelAdmin(admin.ModelAdmin):
        meta = model._meta
        fields = [x.name for x in meta.fields+meta.many_to_many if x.name not in ['id','date','date_mod']]
        displayable_fields = [x.name for x in meta.fields]
        if model.__bases__[0].__name__ == 'Name':
            meta = m.Name._meta
            fields += [x.name for x in meta.fields if x.name != 'id' and x.name not in fields]
        inlines = get_inlines(model)
        list_display = displayable_fields
        not_editable = ['num','id','time','last_update','date_mod','table_html','data']
        list_editable = [field for field in displayable_fields \
                         if field not in not_editable]
        not_linkable = []#'date_mod']
        list_display_links = [field for field in displayable_fields \
                              if field not in list_editable+not_linkable]    
    return GenericModelAdmin

app_path = os.path.dirname(os.path.realpath(__file__))
app_name = os.path.split(app_path)[-1]
print app_name
app_models = get_app(app_name)
for model in get_models(app_models):
    try:
        admin.site.register(model,get_admin(model))
    except AlreadyRegistered:
        pass
        
    