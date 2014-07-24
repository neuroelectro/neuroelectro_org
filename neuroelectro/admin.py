import os
from django.contrib import admin
from django import forms
import models as m
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.db.models import get_app,get_models
from django.contrib.admin.sites import AlreadyRegistered
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

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
        
# Support for allowing social_auth authentication for /admin (django.contrib.admin)
# Found at https://djangosnippets.org/snippets/2856/
if getattr(settings, 'SOCIAL_AUTH_USE_AS_ADMIN_LOGIN', False):

    def _social_auth_login(self, request, **kwargs):
        if request.user.is_authenticated():
            if not request.user.is_active or not request.user.is_staff:
                raise PermissionDenied()
        else:
            return redirect_to_login(request.get_full_path())

    # Overide the standard admin login form.
    admin.sites.AdminSite.login = _social_auth_login
    