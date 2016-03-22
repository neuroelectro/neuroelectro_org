# -*- coding: utf-8 -*-

from crispy_forms.bootstrap import InlineCheckboxes, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit
from neuroelectro import models as m

__author__ = 'stripathy'

# In forms.py...
from django import forms


class DataTableUploadForm(forms.Form):
    table_file = forms.FileField(
        label = "Select a table csv file",
        required = True
    )
    table_name = forms.CharField(
        label = u'Table name (e.g., Table S1)',
        max_length=50,
        required = True
    )
    pmid = forms.CharField(
        max_length=10,
        required = True,
        label = u'Article PMID',
    )
    table_title = forms.CharField(
        label = u'Table title (e.g., Table S1)',
        widget = forms.Textarea(attrs={'rows': 3}),
        max_length=1000,
        required = False
    )
    table_legend = forms.CharField(
        label = u'Table legend',
        widget = forms.Textarea(attrs={'rows': 3}),
        max_length=2000,
        required = False
    )
    associated_text = forms.CharField(
        label = u'Text associated with table',
        widget = forms.Textarea(attrs={'rows': 3}),
        max_length=5000,
        required = False
    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-tablefileupload'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.layout = Layout(
            Fieldset(
                "Upload table and provide provenance",
                'table_file',
                'pmid',
                'table_name',
                'table_title',
                'table_legend',
                'associated_text',
                ),
            FormActions(
                Submit('submit', 'Submit Information', align='middle'),
                )
            )
        super(DataTableUploadForm, self).__init__(*args, **kwargs)


class ArticleFullTextUploadForm(forms.Form):
    full_text_file = forms.FileField(
        label = "Select a full text html file",
        required = True
    )
    pmid = forms.CharField(
        max_length=10,
        required = True,
        label = u'Article PMID',
    )


    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-tablefileupload'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.layout = Layout(
            Fieldset(
                "Upload full text and provide provenance",
                'full_text_file',
                'pmid',
                ),
            FormActions(
                Submit('submit', 'Submit Information', align='middle'),
                )
            )
        super(ArticleFullTextUploadForm, self).__init__(*args, **kwargs)


class ArticleMetadataForm(forms.Form):
    AnimalAge = forms.CharField(
        required = False,
        label = u'Age (days, e.g. 5-10; P46-P94)'
    )
    AnimalWeight = forms.CharField(
        required = False,
        label = u'Weight (grams, e.g. 150-200)'
    )
    RecTemp = forms.CharField(
        required = False,
        label = u'Temp (°C, e.g. 33-45°C)'
    )
    JxnOffset = forms.CharField(
        required = False,
        label = u'Junction Offset (mV, e.g. -11 mV)'
    )
    SpeciesNote = forms.CharField(
        required = False,
        label = u'Note for Species'
    )
    StrainNote = forms.CharField(
        required = False,
        label = u'Note for Strain'
    )
    ElectrodeTypeNote = forms.CharField(
        required = False,
        label = u'Note for Electrode Type'
    )
    PrepTypeNote = forms.CharField(
        required = False,
        label = u'Note for Prep Type'
    )
    AnimalAgeNote = forms.CharField(
        required = False,
        label = u'Note for Animal Age'
    )
    AnimalWeightNote = forms.CharField(
        required = False,
        label = u'Note for Animal Weight'
    )
    RecTempNote = forms.CharField(
        required = False,
        label = u'Note for Temp'
    )
    JxnOffsetNote = forms.CharField(
        required = False,
        label = u'Note for Junction Offset'
    )
    ExternalSolution = forms.CharField(
        widget = forms.Textarea(attrs={'rows': 3}),
        required = False,
        label = u'External (recording, perfusing, ACSF) solution'
    )
    InternalSolution = forms.CharField(
        widget = forms.Textarea(attrs={'rows': 3}),
        required = False,
        label = u'Internal (pipette, electrode) solution'
    )
    JxnPotentialNote = forms.CharField(
        required = False,
        label = u'Note for Junction Potential'
    )
    ExternalSolutionNote = forms.CharField(
        required = False,
        label = u'Note for External solution'
    )
    InternalSolutionNote = forms.CharField(
        required = False,
        label = u'Note for Internal solution'
    )
    MetadataNote = forms.CharField(
        widget = forms.Textarea(attrs={'rows': 3}),
        required = False,
        label = u'General note for metadata curation'
    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-metaDataForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.layout = Layout(
            Fieldset(
                "Assign Metadata",
                'Species',
                'Strain',
                'ElectrodeType',
                'PrepType',
                'SpeciesNote',
                'StrainNote',
                'ElectrodeTypeNote',
                'PrepTypeNote',
                'AnimalAge',
                'AnimalWeight',
                'RecTemp',
                'JxnOffset',
                'AnimalAgeNote',
                'AnimalWeightNote',
                'RecTempNote',
                'JxnOffsetNote',
                'JxnPotential',
                'ExternalSolution',
                'InternalSolution',
                'JxnPotentialNote',
                'ExternalSolutionNote',
                'InternalSolutionNote',
                InlineCheckboxes('NeedsExpert'),
                'MetadataNote',
                ),
            FormActions(
                Submit('submit', 'Submit Information', align='middle'),

                )
            )
        super(ArticleMetadataForm, self).__init__(*args, **kwargs)
        self.fields['Species'] = forms.MultipleChoiceField(
            choices= [(md.id, md.value) for md in m.MetaData.objects.filter(name = 'Species')],
            required = False,
        )
        self.fields['Strain'] = forms.MultipleChoiceField(
            choices=[ (md.id, md.value) for md in m.MetaData.objects.filter(name = 'Strain')],
            required = False,
        )
        self.fields['ElectrodeType'] = forms.MultipleChoiceField(
            choices=[ (md.id, md.value) for md in m.MetaData.objects.filter(name = 'ElectrodeType')],
            required = False,
        )
        self.fields['JxnPotential'] = forms.MultipleChoiceField(
            choices=[ (md.id, md.value) for md in m.MetaData.objects.filter(name = 'JxnPotential')],
            required = False,
        )
        self.fields['PrepType'] = forms.MultipleChoiceField(
            choices=[ (md.pk, md.value) for md in m.MetaData.objects.filter(name = 'PrepType')],
            required = False,
        )
        self.fields['NeedsExpert'] = forms.MultipleChoiceField(
            choices=[('Expert', 'Needs expert review')],
            required = False,
            label = u'Article Metadata Needs Review',
        )


class NeuronConversionForm(forms.Form):
    NeuronName = forms.CharField(
        widget = forms.Textarea(attrs={'rows': 3}),
        required = False,
        label = u'Neuron name query (e.g. Sst-expressing Martinotti cell)'
    )
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-metaDataForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.layout = Layout(
            Fieldset(
                "Please provide a neuron name for query",
                'NeuronName',
                ),
            FormActions(
                Submit('submit', 'Submit Information', align='middle'),

                )
            )
        super(NeuronConversionForm, self).__init__(*args, **kwargs)