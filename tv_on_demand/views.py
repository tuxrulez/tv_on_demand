#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.views.generic import simple
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import simplejson
from tv_on_demand.forms import StructureForm

@permission_required('tv_on_demand.add_structure')
def structure_add(request):
    context = {}
    response = simple.direct_to_template(request,
                                         extra_context=context,
                                         template='tv_on_demand/structure_form.html')

    return response


@permission_required('tv_on_demand.add_structure')    
def structure_ajax_add(request):
    if not request.is_ajax():
        return HttpResponseForbidden('forbbiden')
    
    json_data = {}
    if request.POST:
        form = StructureForm(request.POST, request.FILES)
        
        if form.is_valid():
            instance = form.save()
            json_data['id'] = instance.pk
            json_data['name'] = instance.name
            json_data['template'] = instance.template.url
        
        else:
            json_data['errors'] = form.errors.items()

    return HttpResponse(simplejson.dumps(json_data))