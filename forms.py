#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from mmutils.forms import BRDateTimeField
from tv_on_demand.models import Structure, StructureRow

class StructureForm(forms.ModelForm):
    date_start = BRDateTimeField(label=_('date start'), required=False)
    date_end = BRDateTimeField(label=_('date end'), required=False)
    
    class Meta:
        model = Structure
        exclude = ('content_type', 'object_id', 'external_id')


class StructureRowForm(forms.ModelForm):
    date_start = BRDateTimeField(label=_('date start'))
    date_end = BRDateTimeField(label=_('date end'))
    structure = forms.ModelChoiceField(queryset=Structure.objects.all(),
                                       widget=forms.Select(attrs={'style': 'display: none;'}))
    parent = forms.ModelChoiceField(queryset=StructureRow.objects.all(), required=False,
                                    widget=forms.Select(attrs={'style': 'display: none;'}))
    external_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    order = forms.CharField(widget=forms.HiddenInput)
    
    def clean(self):
        gdata = lambda key: self.cleaned_data.get(key, '')
        ct_number = lambda key: gdata(key) and 1 or 0
        total_content = ct_number('entry') + ct_number('mediafile')
        
        if total_content < 1:
            raise forms.ValidationError(_('you must pick a row content: mediafile or entry'))        

        if total_content > 1:
            raise forms.ValidationError(_('you cannot pick more than one row content'))        
        
        return self.cleaned_data
        
    
    class Meta:
        model = StructureRow
