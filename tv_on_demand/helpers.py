# -*- coding:utf-8 -*-

import os
import time
from datetime import date, datetime, timedelta
from StringIO import StringIO
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.contrib.auth.models import User
from django.http import HttpResponse
from mediafiles.models import MediaFile, MediaDatabase
from tv_on_demand.models import Structure, StructureRow, Skin


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
        
class LiveFileReader(object):

    def __init__(self, base_dir=os.path.join(settings.MODPATH, 'importer', 'tv_on_demand', 'live')):
        self.base_dir = base_dir
        self.allowed_size = getattr(settings, 'LIVE_TV_FILE_SIZE', 5242880)
        settings_time = getattr(settings, 'LIVE_TV_FILE_TIME', 90)
        self.allowed_time = datetime.now() - timedelta(seconds=settings_time)
        self.allowed_exts = ['mp4','avi','mpg','mpg4']
        self.file_path = ''
        self.file_name = ''

    def select_file(self):
        '''Seleciona o último arquivo modificado com tamanho mínimo e tempo de modificação mínimo permitido'''

        file_list = []

        for item in os.listdir(self.base_dir):
            # a cada iteração desse loop uma tupla é inserida no file_list com os seguinte conteúdo:
            # (data_de_modificacao, tamanho_do_arquivo, nome_do_arquivo, caminho_do_arquivo)
            item_path = os.path.join(self.base_dir, item)
            ext = item.split('.')[-2]

            if os.path.isfile(item_path) and ext in self.allowed_exts:
                ftime = time.localtime(os.path.getmtime(item_path))
                file_date = datetime(year=ftime.tm_year, month=ftime.tm_mon, day=ftime.tm_mday, hour=ftime.tm_hour,
                                     minute=ftime.tm_min, second=ftime.tm_sec)
                file_list.append((file_date, os.path.getsize(item_path), item, item_path))

        if not file_list:
            return False

        # esse sort ordena pelo primeiro elemento da tupla, no caso a data de modificação
        file_list.sort()
        # pegamos então o último arquivo modificado com esse slice
        last_modified_file = file_list[-1]

        # se o arquivo não atender os requisitos ele tenta pegar o penúltimo
        if last_modified_file[1] < self.allowed_size or last_modified_file[0] < self.allowed_time:
            try:
                last_modified_file = file_list[-2]
            except IndexError:
                return False

        # se o penúltimo também falhar não tentamos mais, afinal alguma coisa está errada com esses arquivos
        if last_modified_file[1] < self.allowed_size or last_modified_file[0] < self.allowed_time:
            return False

        self.file_path = last_modified_file[3]
        self.file_name = last_modified_file[2]

        return True
