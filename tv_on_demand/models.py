#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from mptt.models import MPTTModel
from django.db import models
from django.contrib.auth.models import Group, User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from django.conf import settings
from sorl.thumbnail import get_thumbnail
from mmutils.common import auto_serialize
from mediafiles.models import MediaFile
from news.models import ENTRY_TYPES


class Skin(models.Model):
    title = models.CharField(_('title'), max_length=45)
    slug = models.SlugField(max_length=45, editable=False)
    external_id = models.PositiveIntegerField(_('external id'), null=True, blank=True)
    accept_video = models.BooleanField()
    accept_audio = models.BooleanField()
    accept_entry = models.BooleanField()
    accept_image = models.BooleanField()
    
    class Meta:
        verbose_name = _('skin')
        verbose_name_plural = _('skins')
        
    def __unicode__(self):
        return self.title
        
    def get_allowed_medias(self):
        formated_val = '%s,%s,%s,%s' %(self.accept_video and 'video' or '', self.accept_audio and 'audio' or '',
                                       self.accept_entry and 'entry' or '', self.accept_image and 'image' or '')
        return formated_val
        
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Skin, self).save(*args, **kwargs)
        
    def logo_thumb(self):
        logo_file = os.path.join(settings.MEDIA_ROOT, 'skins', self.slug, 'logo.jpg')
        thumb = get_thumbnail(logo_file, '160x260', quality=99)                
        return thumb
        

class Structure(models.Model):
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'),
                                     null=True, blank=True)
    object_id = models.PositiveSmallIntegerField(_('object id'), null=True, blank=True)    
    name = models.CharField(_('name'), max_length=100)
    skin = models.ForeignKey(Skin, verbose_name=_('skin'))
    external_id = models.PositiveIntegerField(_('external id'), null=True, blank=True)
    
    content_object = generic.GenericForeignKey(ct_field='content_type', fk_field='object_id')
    
    
    class Meta:
        verbose_name = _('structure')
        verbose_name_plural = _('structures')
        
    def __unicode__(self):
        return self.name
        
    def serialize(self):
        return auto_serialize(self)
        
    @models.permalink
    def get_absolute_url(self):
        return ('admin:tv_on_demand_structure_change', [self.pk])
        
        
class StructureRow(MPTTModel):
    structure = models.ForeignKey(Structure, verbose_name=_('structure'))
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    title = models.CharField(_('title'), max_length=100)
    label = models.TextField(_('description'), null=True, blank=True)
    mediafile = models.ForeignKey(MediaFile, verbose_name=_('media'), null=True, blank=True)
    entry = models.CharField(_('entry'), max_length=45, null=True, blank=True, choices=ENTRY_TYPES)
    date_start = models.DateTimeField(_('date start'))
    date_end = models.DateTimeField(_('date end'))
    external_id = models.PositiveIntegerField(_('external id'), null=True, blank=True)
    order = models.PositiveIntegerField(_('order'))
    groups = models.ManyToManyField(Group, verbose_name=_('allowed groups'), null=True, blank=True)
    users = models.ManyToManyField(User, verbose_name=_('allowed_users'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('row')
        verbose_name_plural = _('rows')
        
    class MPTTMeta:
        order_insertion_by=['order']
        
    def __unicode__(self):
        return self.title
        
    def br_datetime(self, field):
        value = getattr(self, field)
        return value.strftime('%d/%m/%Y %H:%M')
        
    def serialize(self):
        return auto_serialize(self, datetime_format='%d/%m/%Y %H:%M') 
        
    def restricted(self):
        #retorna se o objeto tem restrições de usuários ou não
        return self.users.all() and True or False    
    
    
    
      
