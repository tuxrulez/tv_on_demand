#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from mmutils.forms import BRDateTimeField
from tv_on_demand.models import Structure

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
