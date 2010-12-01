#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tv_on_demand.models import Structure

def structure_processor(request):
    structure = Structure.objects.all()[0]
    
    return {'structure': structure}
