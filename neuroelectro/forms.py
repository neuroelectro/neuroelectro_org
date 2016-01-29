__author__ = 'stripathy'

# In forms.py...
from django import forms


class TableFileForm(forms.Form):
    title = forms.CharField(max_length=50, required = False)
    table_file = forms.FileField(label = "select a table csv file")
    pmid = forms.CharField(max_length=10, required = False)
    full_text_file = forms.FileField(label = "select a file text html file", required = False)