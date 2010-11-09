#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.views.generic.create_update import create_object, update_object
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from tv_on_demand.forms import StructureForm, StructureRowForm
from tv_on_demand.models import Structure, StructureRow

@permission_required('tv_on_demand.add_structure')
@permission_required('tv_on_demand.change_structure')
@permission_required('tv_on_demand.add_structurerow')
@permission_required('tv_on_demand.change_structurerow')
@permission_required('tv_on_demand.delete_structurerow')
def structure_add(request):
    response = create_object(request, form_class=StructureForm)
    return response
    
@permission_required('tv_on_demand.add_structure')
@permission_required('tv_on_demand.change_structure')
@permission_required('tv_on_demand.add_structurerow')
@permission_required('tv_on_demand.change_structurerow')
@permission_required('tv_on_demand.delete_structurerow')    
def structure_change(request, object_id):
    response = update_object(request, form_class=StructureForm,
                             object_id=object_id,
                             extra_context={'row_form': StructureRowForm()})
    return response
    

def generic_structure_ajax(request, modelform, **kwargs):
    if not request.is_ajax():
        return HttpResponseForbidden('forbbiden')
        
    json_data = {}
    if request.POST:
        form = modelform(request.POST, request.FILES, **kwargs)
        
        if form.is_valid():
            instance = form.save()
            json_data = instance.serialize()
            json_data['media_type'] = instance.mediafile.media_type       
        else:
            json_data['errors'] = form.errors.items()

    return HttpResponse(simplejson.dumps(json_data))


@permission_required('tv_on_demand.add_structurerow')
def structurerow_ajax_add(request):
    return generic_structure_ajax(request, StructureRowForm)
    
    
@permission_required('tv_on_demand.change_structurerow')
def structurerow_ajax_change(request, object_id):       
    structurerow = get_object_or_404(StructureRow, pk=object_id)       
    return generic_structure_ajax(request, StructureRowForm, instance=structurerow)
    

@permission_required('tv_on_demand.delete_structurerow')
def structurerow_ajax_delete(request, object_id):
    if not request.is_ajax():
        return HttpResponseForbidden('forbidden')
    
    instance = get_object_or_404(StructureRow, pk=object_id)
    instance.delete()
    
    return HttpResponse('deleted')
    
    
    
    
    
