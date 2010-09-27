#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mptt
from mptt.models import MPTTModel
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from mediafiles.models import MediaFile
from quizzes.models import Question
from news.models import ENTRY_TYPES


class Structure(models.Model):
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'),
                                     null=True, blank=True)
    object_id = models.PositiveSmallIntegerField(_('object id'), null=True, blank=True)    
    name = models.CharField(_('name'), max_length=100)
    template = models.FileField(_('template'), max_length=255, upload_to='tv_on_demand/structure/template')
    external_id = models.PositiveIntegerField(_('external id'), null=True, blank=True)
    
    content_object = generic.GenericForeignKey(ct_field='content_type', fk_field='object_id')
    
    
    class Meta:
        verbose_name = _('structure')
        verbose_name_plural = _('structures')
        
    def __unicode__(self):
        return self.name
        
        
class StructureRow(MPTTModel):
    structure = models.ForeignKey(Structure, verbose_name=_('structure'))
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    title = models.CharField(_('title'), max_length=100)
    label = models.CharField(_('description'), max_length=100, null=True, blank=True)
    mediafile = models.ForeignKey(MediaFile, verbose_name=_('media'), null=True, blank=True)
    question = models.ForeignKey(Question, verbose_name=_('question'), null=True, blank=True)
    entry = models.CharField(_('entry'), max_length=45, null=True, blank=True, choices=ENTRY_TYPES)
    date_start = models.DateTimeField(_('date start'))
    date_end = models.DateTimeField(_('date end'))
    external_id = models.PositiveIntegerField(_('external id'), null=True, blank=True)
    order = models.PositiveIntegerField(_('order'))
    
    class Meta:
        verbose_name = _('row')
        verbose_name_plural = _('rows')
        
    class MPTTMeta:
        order_insertion_by=['order']
        
    def __unicode__(self):
        return self.title
        
