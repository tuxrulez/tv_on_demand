#/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from threading import Thread
from django.conf import settings
from django.views.generic.create_update import create_object, update_object
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, Http404
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.template import TemplateDoesNotExist
from pyamf.remoting.gateway.django import DjangoGateway
from tv_on_demand.forms import StructureForm, StructureRowForm
from tv_on_demand.models import Structure, StructureRow
from tv_on_demand.helpers import LiveFileReader
from clients.models import Store

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

            #salva os usuários, se houverem grupos
            for group in instance.groups.all():
                for user_group in group.user_set.all():
                    instance.users.add(user_group)

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


def do_logout(request):
    logout(request)
    return HttpResponse('ok')


def amf_rows(request, amf_data):
    try:
        structure_id = amf_data['structure_id']
        structure = Structure.objects.get(pk=structure_id)
    except KeyError:
        print 'structure_id key error'
        return ''
    except Structure.DoesNotExist:
        print 'structure_id not found'
        return ''

    parent_id = amf_data.get('parent_id', '')
    if not parent_id:
        rows = StructureRow.objects.filter(parent=None, structure=structure).order_by('order')
    else:
        try:
            parent = StructureRow.objects.get(pk=parent_id)
        except StructureRow.DoesNotExist:
            return ''
        rows = StructureRow.objects.filter(parent=parent, structure=structure).order_by('order')

    amf_output = []
    for row in rows:
        local_data = {'id': row.pk, 'title': row.title, 'description': row.label, 'type': row.mediafile.media_type,
                      'file': row.mediafile.path and row.mediafile.path.url or '', 'structure_id': row.structure.id,
                      'restricted': False,
                      'video_image': row.mediafile.video_image and row.mediafile.video_image.url or ''}
        if row.mediafile.media_type == 'video':
            local_data['video_play_url'] = reverse('player_single', args=[row.id, row.mediafile.pk])

        amf_output.append(local_data)
    return amf_output


def amf_verify_user(request, amf_data):
    try:
        requested_row = StructureRow.objects.get(pk=amf_data['row_id'])
    except KeyError:
        return False
    except StructureRow.DoesNotExist:
        return False

    if not request.user in requested_row.users.all():
        return False

    return True


def amf_login(request, amf_data):
    try:
        row = StructureRow.objects.get(pk=amf_data['row_id'])
    except KeyError:
        return False
    except StructureRow.DoesNotExist:
        return False

    username = amf_data.get('username', '')
    password = amf_data.get('password', '')

    user = authenticate(username=username, password=password)

    if user != None:
        if user.is_active and user in row.users.all():
            login(request, user)
            return True
        else:
            return False

    return False


def home(request):
    wait_page_url = reverse(request.GET.get('wait_page', 'call_tv_wall'))
    live_channels = ''
    for item_channel in getattr(settings, 'CHANNELS', []):
        live_channels += '%s;%s,' % (item_channel[0], item_channel[2])
    
    store_structure = Store.objects.get(slug=getattr(settings, 'STORE_SLUG')).structure.pk
    structure = get_object_or_404(Structure, id=store_structure)
    context = {'structure': structure, 'wait_page_url': wait_page_url, 'live_channels': live_channels[:-1]}
    
    return direct_to_template(request, template='tv_on_demand/flash_home.html',
                              extra_context=context)


def format_screen(request):
    #focus
    os.system("xte -x :0.0 'mousemove 10 10' 'mousedown 1' 'mouseup 1'")
    return HttpResponse('ok')
    


amf_services = {
    'structure.rows': amf_rows,
    'structure.verify_user': amf_verify_user,
    'structure.login': amf_login,
}

amf_structure = DjangoGateway(amf_services)

