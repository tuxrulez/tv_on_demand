#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.views.generic import simple
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from tv_on_demand.forms import StructureForm
from tv_on_demand.models import Structure

@permission_required('tv_on_demand.add_structure')
@permission_required('tv_on_demand.change_structure')
@permission_required('tv_on_demand.add_structurerow')
@permission_required('tv_on_demand.change_structurerow')
def structure_add(request):
    context = {}
    response = simple.direct_to_template(request,
                                         extra_context=context,
                                         template='tv_on_demand/structure_form.html')

    return response


def generic_structure_ajax(request, **kwargs):
    json_data = {}
    if request.POST:
        form = StructureForm(request.POST, request.FILES, **kwargs)
        
        if form.is_valid():
            instance = form.save()
            json_data['id'] = instance.pk
            json_data['name'] = instance.name
            json_data['template'] = instance.template.url
        
        else:
            json_data['errors'] = form.errors.items()

    return HttpResponse(simplejson.dumps(json_data))


@permission_required('tv_on_demand.add_structure')    
def structure_ajax_add(request):
    if not request.is_ajax():
        return HttpResponseForbidden('forbbiden')
    
    return generic_structure_ajax(request)
    

@permission_required('tv_on_demand.change_structure')
def structure_ajax_change(request, object_id):
    if not request.is_ajax():
        return HttpResponseForbidden('forbidden')
        
    structure = get_object_or_404(Structure, pk=object_id)
    
    return generic_structure_ajax(request, instance=structure)


@permission_required('tv_on_demand.add_structurerow')
def structurerow_ajax_add(request):
    if not request.is_ajax():
        return HttpResponseForbidden('forbidden')
    
    return HttpResponse('hello') 
    
    
    
    
    
    
    