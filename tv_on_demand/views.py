#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from django.conf import settings
from django.views.generic.create_update import create_object, update_object
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.template import TemplateDoesNotExist
from tv_on_demand.forms import StructureForm, StructureRowForm
from tv_on_demand.models import Structure, StructureRow
from tv_on_demand.helpers import LiveFileReader

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
            if instance.mediafile:
                json_data['media_type'] = instance.mediafile.media_type
            else:
                json_data['media_type'] = ''
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
    
def generic_main(request, structure_id, template='tv_on_demand/main.html'):
    structure = get_object_or_404(Structure, pk=structure_id)
    root_rows = StructureRow.objects.filter(parent=None, structure=structure).order_by('order')
    context = {'structure': structure,
               'root_rows': root_rows}
    
    response = direct_to_template(request, template=template, extra_context=context)
    return response    
    
    
def main(request, structure_id):
    return generic_main(request, structure_id)
    

def pure_main(request, structure_id):
    return generic_main(request, structure_id, template='tv_on_demand/pure_main.html')
    

def children_of(request, father_id):
    father_row = get_object_or_404(StructureRow, pk=father_id)
    allowed_users = father_row.users.all()
    
    # TODO: fazer verificação para os filhos
    
    if allowed_users:
        if not request.user.is_authenticated():
            return HttpResponse('not_allowed')
            
        if not request.user in allowed_users:
            return HttpResponse('not_allowed')
    
    rows = father_row.children.all()
    context = {'rows': rows, 'father_row': father_row}
    
    client_tmpl = 'tv_on_demand/%s/rows.html' % father_row.structure.skin.slug

    try:
        response = direct_to_template(request, template=client_tmpl, extra_context=context)
    except TemplateDoesNotExist:
        response = direct_to_template(request, template='tv_on_demand/rows.html', extra_context=context)
        
    return response
    
    
def serve_video(request, row_id, video_id):
    cur_row = get_object_or_404(StructureRow, pk=row_id)
    rows = cur_row.children.filter(mediafile__media_type='video')
    selected_row = get_object_or_404(StructureRow, pk=video_id)
    
    context = {'rows': rows, 'selected_row': selected_row, 'father_row': cur_row}
    response = direct_to_template(request, template='tv_on_demand/video_list.html', extra_context=context)
    return response
    
    
def live_media(request, filename):
    # serve um vídeo direto do diretório importer/tv_on_demand/live
    # baseado no nome do arquivo via GET
    file_path = os.path.join(settings.MODPATH, 'importer', 'tv_on_demand', 'live', filename)
  
    if not os.path.exists(file_path):
        return HttpResponseForbidden('file does not exist')
        
    file_ext = filename.split('.')[-2]
    if file_ext == 'avi':
        mime_type = 'video/x-msvideo'
    else:
        mime_type = 'video/mpeg'
    
    file_media = open(file_path, 'r').read()
    
    response = HttpResponse(file_media, mimetype=mime_type)
    return response
    
    
def live(request):
    live_reader = LiveFileReader()
    live_reader.select_file()
    
    context = {'live_filename': live_reader.file_name or 'nofile'}
    response = direct_to_template(request, template='tv_on_demand/live.html', extra_context=context)
    
    return response
    
    
def do_login(request, row_id):
    row = get_object_or_404(StructureRow, pk=row_id)    
    
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        user = authenticate(username=username, password=password)
        
        if user != None:
            if user.is_active and user in row.users.all():                
                login(request, user)
                response = HttpResponse('login_true')
            else:
                response = HttpResponse('login_false')
                
        else:
            response = HttpResponse('login_false')
            
    else:
        response = direct_to_template(request, template='tv_on_demand/login.html',
                                      extra_context={'row_url': reverse('tod_login', args=[row_id])})
        
    return response
    
    
def do_logout(request):
    logout(request)
    return HttpResponse('ok')
  
