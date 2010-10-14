# -*- coding:utf-8 -*-

import os
from datetime import date
from StringIO import StringIO
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core.management import call_command
from tv_on_demand.models import Structure,StructureRow


class ExportToLog(object):

    def __init__(self, related_object=None,log_format='json'):
        self.related_object = related_object
        self.log_format = log_format
        self.path = self.set_path() 
        self._make_path()
        self.historylog_path = self.set_historylog_path()
        self.get_queryset()
    
    def set_path(self):
        base_path = getattr(settings, 'LOGS_EXPORT_PATH', 'exporter')
        
        if not self.related_object:        
            path = os.path.join(settings.MODPATH, base_path, 'logs')
        else:
            opts = self.related_object._meta
            i_object = getattr(self.related_object, 'slug', str(self.related_object.pk))
            path = os.path.join(settings.MODPATH, base_path, 'logs', opts.app_label, opts.module_name, i_object)
        return path
        
    def set_historylog_path(self):
        filename = '%s.%s' % ( date.today(), self.log_format)
        return os.path.join(self.path, filename)
        
    def _make_path(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
           
    def get_queryset(self):
        if not self.related_object:
            return Structure.objects.all()
            
        ctype = ContentType.objects.get_for_model(self.related_object)

        structure = Structure.objects.filter(content_type=ctype,object_id=self.related_object.pk)
        rows = StructureRow.objects.filter(structure=structure)

        qs =[]
        qs.append(structure)
        qs.append(rows)

        return qs

    def export(self):
        qs = self.get_queryset()
        out = open(self.historylog_path, 'wb')

        if self.related_object:
            for instance in qs:
                data = serializers.serialize(self.log_format, instance)
                out.write(data)
        else:
            data = serializers.serialize(self.log_format, qs)
            out.write(data)
        out.close()

        return data
