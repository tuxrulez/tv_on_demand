#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, date
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from clients.models import Chain, Store
from mediafiles.models import MediaFile, MediaDatabase


class Skin(models.Model):
    title = models.CharField(_('title'), max_length=45)
    slug = models.SlugField(max_length=45, editable=False)
    
    class Meta:
        verbose_name = _('skin')
        verbose_name_plural = _('skins')
        
    def __unicode__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        try:
            super(Skin, self).save(*args, **kwargs)
        except:
            pass
        
        

class Structure(models.Model):
    name = models.CharField(_('name'), max_length=100)
    skin = models.ForeignKey(Skin, verbose_name=_('skin'))    
    mediadatabase = models.ForeignKey(MediaDatabase, verbose_name=_('media database'))
    chain = models.ForeignKey(Chain, verbose_name=_('chain'), null=True, blank=True)
    store = models.ForeignKey(Store, verbose_name=_('store'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('structure')
        verbose_name_plural = _('structures')
        
    def __unicode__(self):
        return self.name


class StructureRowManager(models.Manager):
    
    def active(self):
        now = datetime.now().strftime('%H:%M:%S')
        today = date.today()
        return self.filter(mediafile__date_start__lte=today, mediafile__date_end__gte=today,
                           mediafile__time_start__lte=now, mediafile__time_end__gte=now)
        
        
class StructureRow(models.Model):
    structure = models.ForeignKey(Structure, verbose_name=_('structure'))
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    title = models.CharField(_('title'), max_length=100)
    label = models.TextField(_('description'), null=True, blank=True)
    mediafile = models.ForeignKey(MediaFile, verbose_name=_('media'), null=True, blank=True)
    order = models.PositiveIntegerField(_('order'))
    objects = StructureRowManager()
    
    class Meta:
        verbose_name = _('row')
        verbose_name_plural = _('rows')
        
    def __unicode__(self):
        return self.title
  
