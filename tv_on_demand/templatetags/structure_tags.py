#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.inclusion_tag('tv_on_demand/widgets/structure_formfields.html')
def structure_as_p(form, exclude='', instance=None, **kwargs):
    exclude_list = exclude.split(',')
    return {'form': form, 'exclude_list': exclude_list,
            'instance': instance}
    
    