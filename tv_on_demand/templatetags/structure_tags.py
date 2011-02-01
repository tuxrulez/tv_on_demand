#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import template
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from mmutils.tags import quick_tag
from news.models import ENTRY_TYPES
from tv_on_demand.forms import StructureRowForm

register = template.Library()

@register.inclusion_tag('tv_on_demand/widgets/structure_formfields.html')
def structure_as_p(form, exclude='', instance=None, **kwargs):
    exclude_list = exclude.split(',')
    return {'form': form, 'exclude_list': exclude_list,
            'instance': instance}


def item_content(instance):
    media_type = instance.mediafile and instance.mediafile.media_type or 'news'    
    
    entry_content = '<select name="fake_entry">'
    if not instance.entry:
        entry_content += '<option value="" selected="selected">---------</option>'
    else:
        entry_content += '<option value="">---------</option>'    
   
    for entry in ENTRY_TYPES:
        if instance.entry == entry[0]:
            entry_content += '<option value="%s" selected="selected">%s</option>' %(entry[0], entry[1].capitalize())
        else:
            entry_content += '<option value="%s">%s</option>' %(entry[0], entry[1].capitalize())    
    entry_content += '</select>'
    
    content = u'''
    <li>
        <a href="#" class="media-link" target="_blank">
            <img src="/media/style/%(row_icon)s.png">
        </a><br />
        <a href="%(item_url)s" class="view-item">Ver</a> / 
        <a href="#" class="properties">Editar</a> / 
        <a href="#" class="row-rm">Remover</a>
        <p class="edit ghost">
            <strong>Selecione um tipo de item</strong> <br />
            <a href="/admin/mediafiles/mediafile/" class="select-media">Mídia</a> <br />''' %{'row_icon': media_type, 'title': instance.title, 'label': instance.label, 'date_start': instance.br_datetime('date_start'),
               'date_end': instance.br_datetime('date_end'), 'media_id': instance.mediafile and instance.mediafile.pk or '', 'item_url': reverse('admin:mediafiles_mediafile_change', args=[instance.mediafile.pk]),
               'order': instance.order, 'object_id': instance.pk, 'parent': instance.parent and instance.parent.pk or '', 'entries': entry_content}
            
    if instance.structure.skin.accept_entry:
        content += u'''Notícia: <br /> 
                   %s<br /> <br />''' % entry_content
                   
    content += u'''<span class="ghost" style="display: inline; ">
                Título<br /> 
                <input type="text" name="fake_title" value="%(title)s" /> <br />
                Descrição<br /> 
                <input type="text" name="fake_description" value="%(label)s" /> <br />
                Data de início<br /> 
                <input type="text" name="fake_date_start" value="%(date_start)s" /> <br />
                Data de término<br /> 
                <input type="text" name="fake_date_end" value="%(date_end)s" /> <br />
                <input type="hidden" name="fake_media_id" value="%(media_id)s" />
                <input type="hidden" name="fake_order" value="%(order)i" />
                <input type="hidden" name="fake_object_id" value="%(object_id)i" />
                <input type="hidden" name="fake_parent" value="%(parent)s" />
                <input type="button" name="save" value="Salvar" class="save" />
            </span>
        </p>
    </li>''' %{'row_icon': media_type, 'title': instance.title, 'label': instance.label, 'date_start': instance.br_datetime('date_start'),
               'date_end': instance.br_datetime('date_end'), 'media_id': instance.mediafile and instance.mediafile.pk or '', 'item_url': reverse('admin:mediafiles_mediafile_change', args=[instance.mediafile.pk]),
               'order': instance.order, 'object_id': instance.pk, 'parent': instance.parent and instance.parent.pk or '', 'entries': entry_content}
        
    return content
    

def menu_content(instance):
    user_ids = [u.pk for u in instance.users.all()]
    
    user_content = '<select multiple="multiple" name="users" id="id_users">'
    for user in User.objects.all():
        if user.pk in user_ids:
            user_content += '<option value="%i" selected="selected">%s</option>' %(user.pk, user.username)
        else:
            user_content += '<option value="%i">%s</option>' %(user.pk, user.username)            
    user_content += '</select>'
    
    content = u'''
    <h2>
        <span>%(title)s</span>
        <em>
            <a href="#" class="menu-properties">Editar</a> / 
            <a href="#" class="level-add">Nível [+]</a> / 
            <a href="#" class="row-add">Item [+]</a> /
            <a href="#" class="level-rm">Nível [-]</a>
        </em>
                        
        <p class="ghost">
            <a href="/admin/mediafiles/mediafile/?media_type__exact=menu" class="select-media">Selecionar um menu</a> <br /><br />
            <span class="ghost" style="display: block;">
                Título<br /> <input type="text" name="fake_title" value="%(title)s" /> <br />
                Descrição<br /> <input type="text" name="fake_description" value="%(label)s" /> <br />
                Usuários permitidos<br /> 
                %(users)s<br />
                Data de início<br> <input type="text" name="fake_date_start" value="%(date_start)s" /> <br />
                Data de término<br> <input type="text" name="fake_date_end" value="%(date_end)s" /> <br />
                <input type="hidden" name="fake_media_id" value="%(media_id)s" />
                <input type="hidden" name="fake_order" value="%(order)i" /> 
                <input type="hidden" name="fake_object_id" value="%(object_id)i" />
                <input type="hidden" name="fake_parent" value="%(parent)s" />
                <input type="button" name="save_menu" value="Salvar" class="save" />
            </span>
        </p>
    </h2>''' %{'title': instance.title, 'label': instance.label, 'date_start': instance.br_datetime('date_start'),
               'date_end': instance.br_datetime('date_end'), 'media_id': instance.mediafile and instance.mediafile.pk or '',
               'order': instance.order, 'object_id': instance.pk, 'users': user_content, 'parent': instance.parent and instance.parent.pk or ''}
                    
    return content



def parse_rows(queryset):
    u'''Função recursiva que cria recria a estrutura (html) já salva'''
    
    row_content = ''
    
    for row in queryset:
        row_type = row.mediafile and row.mediafile.media_type or None                
        if row_type == 'menu':
            row_content += '<div>'
            row_content += menu_content(row)
            
            children_items = row.get_children().exclude(mediafile__media_type='menu').order_by('order')
            if children_items:
                row_content += '<ul>'
                row_content += parse_rows(children_items)
                row_content += '</ul>'
            
            children_menus = row.get_children().filter(mediafile__media_type='menu').order_by('order')
            if children_menus:
                row_content += parse_rows(children_menus)
                        
            row_content += '</div>'
            
        else:
            row_content += item_content(row)           

            
    return row_content
            
    
            
@register.tag
@quick_tag
def load_structurerows(context, structure_instance):
    rows = structure_instance.structurerow_set.filter(parent=None).order_by('order')
    if not rows:
        context['rows_output'] = ''
        return ''
    
    context['rows_output'] = parse_rows(rows)
    return ''
    
    
