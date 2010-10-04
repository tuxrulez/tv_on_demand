#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from mmutils.forms import BRDateTimeField
from tv_on_demand.models import Structure, StructureRow

class StructureForm(forms.ModelForm):
    date_start = BRDateTimeField(label=_('date start'), required=False)
    date_end = BRDateTimeField(label=_('date end'), required=False)
    users = forms.ModelMultipleChoiceField(label=_('allowed users'), queryset=User.objects.all(),
                                           required=False)
    
    def clean_template(self):
        template = self.cleaned_data.get('template', '')
        if template.name.split('.')[-1] != 'swf':
            raise forms.ValidationError(_('template must be a swf file'))        
        
        return template
    
    
    class Meta:
        model = Structure
        exclude = ('content_type', 'object_id', 'external_id')


class StructureRowForm(forms.ModelForm):
    date_start = BRDateTimeField(label=_('date start'), required=True)
    date_end = BRDateTimeField(label=_('date end'), required=True)
    
    def clean(self):
        gdata = lambda key: self.cleaned_data.get(key, '')
        ct_number = lambda key: gdata(key) and 1 or 0
        total_content = ct_number('entry') + ct_number('mediafile') + ct_number('question')
        
        if total_content < 1:
            raise forms.ValidationError(_('you must pick a row content: mediafile, entry or question'))        

        if total_content > 1:
            raise forms.ValidationError(_('you cannot pick more than one row content'))        
        
        return self.cleaned_data
        
    
    class Meta:
        model = StructureRow