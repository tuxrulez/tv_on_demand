#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tv_on_demand.models import Structure

def structure_processor(request):
    try:
        structure = Structure.objects.all()[0]
    except IndexError:
        return {}        
    
    return {'structure': structure}
