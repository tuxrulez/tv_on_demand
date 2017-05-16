#/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
from datetime import datetime
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
from django.core.exceptions import MultipleObjectsReturned
from django.template import TemplateDoesNotExist
from pyamf.remoting.gateway.django import DjangoGateway
from tv_on_demand.forms import StructureForm, StructureRowForm
from tv_on_demand.models import Structure, StructureRow
from tv_on_demand.helpers import LiveFileReader
from mediafiles.models import MediaFile
from clients.models import Store, StoreMediaLog
from mediafiles.models import Quiz, QuizOption, QuizStats

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
        rows = StructureRow.objects.active().filter(parent=None, structure=structure).order_by('order')
    else:
        try:
            parent = StructureRow.objects.get(pk=parent_id)
        except StructureRow.DoesNotExist:
            return ''
        rows = StructureRow.objects.active().filter(parent=parent, structure=structure).order_by('order')

    amf_output = []
    for row in rows:
        if row.mediafile:
            if row.mediafile.path:
                if not os.path.exists(row.mediafile.path.path):
                    continue

            if row.mediafile.video_image:
                if not os.path.exists(row.mediafile.video_image.path):
                    continue

        local_data = {'id': row.pk, 'title': row.title, 'description': row.label, 'type': row.mediafile.media_type,
                      'file': row.mediafile.path and row.mediafile.path.url or '', 'structure_id': row.structure.id,
                      'restricted': False,
                      'video_image': row.mediafile.video_image and row.mediafile.video_image.url or ''}

        quiz = row.mediafile.quiz
        if quiz:
            local_data['quiz_id'] = quiz.pk
            local_data['quiz_question'] = quiz.title
            local_data['quiz_options'] = [{'option': o.title, 'correct': o.right_option, 'option_id': o.pk} for o in quiz.quizoption_set.all().order_by('order')]


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


def home(request, structure_id=None, is_promo=None):
    
    chain_slug = getattr(settings, 'CHAIN_SLUG', 'deploy')
    
    if chain_slug == 'deploy':
        deploy = True
    else:
        deploy = False
        
    special_home = getattr(settings, 'SPECIAL_HOME', False)
    
    if special_home and not is_promo:
        flash = 'special_%s.swf' %chain_slug
        context = {'title': 'Special Flash', 'flash': flash, 'deploy': deploy}
        return direct_to_template(request, template='tv_on_demand/special/flash_special.html', extra_context=context)
    
    live_channels = ''
    for item_channel in getattr(settings, 'CHANNELS', []):
        live_channels += '%s;%s,' % (item_channel[0], item_channel[2])
    
    store_slug = ''
    if not structure_id:
        if is_promo:
            wait_page_url = '/'
        else:
            wait_page_url = reverse(request.GET.get('wait_page', 'call_tv_wall'))
        store_slug = getattr(settings, 'STORE_SLUG', 'not-found')
        try:
            structure = Structure.objects.filter(store__slug=store_slug)[0]
        except IndexError:
            raise Http404('structure not found')
    else:
        wait_page_url = '/'
        try:
            structure = Structure.objects.get(pk=structure_id)
        except Structure.DoesNotExist:
            raise Http404('structure not found')

    client_password = structure.password or '123' 

    context = {'structure': structure, 'wait_page_url': wait_page_url, 'live_channels': live_channels[:-1],
              'client_password': client_password, 'deploy': deploy}
    
    return direct_to_template(request, template='tv_on_demand/flash_home.html',
                              extra_context=context)


def quiz_answer(request, quiz_id, option_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    option = get_object_or_404(QuizOption, pk=option_id)

    QuizStats.objects.create(quiz=quiz, option=option)
    return HttpResponse('ok')
    
def full_views_verify(row):
    childrens =  StructureRow.objects.filter(parent=row)
    if not childrens:
        return False
    for children in childrens:
        media_logs = StoreMediaLog.objects.filter(mediafile=children.mediafile)
        if not media_logs:
            return False
        for media_log in media_logs:
            if media_log.full_views_number != 0:
                pass
            else:
                return False
    return True
        
def view_verify(request, amf_data):
    row_id = amf_data.get('row_id', None)
    if not row_id:
        return HttpResponse('not row id')
    try:
        row = StructureRow.objects.get(id=row_id)
    except StructureRow.DoesNotExist:
        return HttpResponse('row not exists')
    if row.mediafile.quiz == None:
        return False
    try:
        quiz_instance = QuizStats.objects.get(quiz=row.mediafile.quiz)
        return False
    except MultipleObjectsReturned:
        return False
    except QuizStats.DoesNotExist:
        pass
    if row.mediafile.media_type == 'video':
        return True

    return full_views_verify(row)

def format_screen(request):
    #focus
    time.sleep(2)
    os.system("xte -x :0.0 'mousemove 10 10' 'mousedown 1' 'mouseup 1'")
    return HttpResponse('ok')
    

def entries_list(request):
    
    data = list()
    for entry in MediaFile.objects.active().filter(media_type='entry').order_by('-date_start', '-time_start')[:20]:
        sub_data = {'title': entry.title, 'label': entry.label,
                    'time': entry.time_start.strftime('%H:%M:%S'),
                    'date': entry.date_start.strftime('%d/%m/%Y')} 
        data.append(sub_data)
        
    response = simplejson.dumps(data)
    
    return HttpResponse(response)
    

amf_services = {
    'structure.rows': amf_rows,
    'structure.view_verify': view_verify,
    'structure.verify_user': amf_verify_user,
    'structure.login': amf_login,
}

amf_structure = DjangoGateway(amf_services)
