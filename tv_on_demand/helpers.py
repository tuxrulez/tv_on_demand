# -*- coding:utf-8 -*-

import os
import time
from datetime import date, datetime, timedelta
from StringIO import StringIO
from xml.etree import cElementTree as ElementTree
from elementtree.ElementTree import parse
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


class TodToXml(object):

    def __init__(self, structure, model_ref=None, rootpath=None):
        ''' structure: a instance of Structure model to export
            model_ref: Should be a related model like a foreign key to Structure, if given
                       it will customize the save_path like <your_project_path>/exporter/tv_on_demand/<module_name>
                       where module_name follows the module name of your model.
            usage: exporter = TodToXml(structure_instance, model_ref=MyRelatedModel)
                   exporter.save()
        '''
        self.rootpath = rootpath
        self.structure = structure
        self.model_ref = model_ref
        self.opts = self.structure._meta
        self.save_path = self._set_path()
        self.xml_path = self._set_xml_path()

    def _set_path(self):

        if not self.rootpath:
            path = os.path.join(settings.MODPATH, 'exporter', self.opts.app_label)

            ref_opts = getattr(self.model_ref, '_meta', None)
            if ref_opts:
                path = os.path.join(path, ref_opts.module_name)
        else:
            path = os.path.join(settings.MODPATH, self.rootpath)

        return path

    def _set_xml_path(self):
        return os.path.join(self.save_path, '%s.xml' %(self.opts.module_name))


    def _parse_rows(self, row_queryset, parent_node):
        fix_date = lambda date: date.strftime('%Y-%m-%d %H:%M:%S')

        for row in row_queryset:
            row_element = ElementTree.SubElement(parent_node, 'row', id=str(row.pk))
            row_parent = ElementTree.SubElement(row_element, 'parent')
            row_parent.text = row.parent and str(row.parent.id) or None
            row_title = ElementTree.SubElement(row_element, 'title')
            row_title.text = row.title
            row_label = ElementTree.SubElement(row_element, 'label')
            row_label.text = row.label
            row_entry = ElementTree.SubElement(row_element, 'entry')
            row_entry.text = row.entry
            row_order = ElementTree.SubElement(row_element, 'order')
            row_order.text = str(row.order)

            usernames = []
            for group_instance in row.groups.all():
                for user_instance in group_instance.user_set.all():
                    # TODO: melhorar isso, evita-se que um usuário que pertença
                    # à outros grupos seja incluido novamente
                    if user_instance.username in usernames:
                        continue

                    row_user = ElementTree.SubElement(row_element, 'user')

                    user_name = ElementTree.SubElement(row_user, 'username')
                    user_name.text = user_instance.username
                    user_passwd = ElementTree.SubElement(row_user, 'password')
                    user_passwd.text = user_instance.password
                    user_email = ElementTree.SubElement(row_user, 'email')
                    user_email.text = user_instance.email

                    usernames.append(user_instance.username)


            mf = row.mediafile
            if mf:
                try:
                    real_path = mf.path.url
                except ValueError:
                    real_path = ''
                try:
                    video_image_url = mf.video_image.url
                except ValueError:
                    video_image_url = ''
                ElementTree.SubElement(row_element, 'mediafile', id=str(mf.pk), media_type=mf.media_type,
                                       title=mf.title, label=mf.label, path=real_path, created=fix_date(mf.created),
                                       video_image=video_image_url, duration=str(mf.duration))
            else:
                ElementTree.SubElement(row_element, 'mediafile')

            row_date_start = ElementTree.SubElement(row_element, 'date_start')
            row_date_start.text = fix_date(row.date_start)
            row_date_end = ElementTree.SubElement(row_element, 'date_end')
            row_date_end.text = fix_date(row.date_end)

            for group in row.groups.all():
                row_group = ElementTree.SubElement(row_element, 'group', name=group.name)
                #TODO: implementar loop de users

            children_qs = row.get_children()
            if children_qs:
                self._parse_rows(children_qs, row_element)


    def _generate(self):
        instance = self.structure

        root = ElementTree.Element('structure')
        structure_id = ElementTree.SubElement(root, 'id')
        structure_id.text = str(instance.pk)
        structure_name = ElementTree.SubElement(root, 'name')
        structure_name.text = instance.name
        structure_skin = ElementTree.SubElement(root, 'skin')
        structure_skin_title = ElementTree.SubElement(structure_skin, 'title')
        structure_skin_title.text = instance.skin.title
        structure_skin_slug = ElementTree.SubElement(structure_skin, 'slug')
        structure_skin_slug.text = instance.skin.slug
        structure_skin_external_id = ElementTree.SubElement(structure_skin, 'external_id')
        structure_skin_external_id.text = str(instance.skin.pk)
        structure_mediadatabase = ElementTree.SubElement(root, 'mediadatabase', name=instance.mediadatabase.name,
                                                                                slug=instance.mediadatabase.slug)

        row_qs = instance.structurerow_set.filter(parent=None)
        self._parse_rows(row_qs, root)

        return ElementTree.ElementTree(root)


    def save(self):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        xml_file = open(self.xml_path, 'wb')
        self._generate().write(xml_file)
        xml_file.close()


class XmlToTod(object):

    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.xml = parse(self.xml_path).getroot()

    def fix_media_url(self, url):
        '''rebuild /media/path/path/file.css to path/path/file.css
           django does not work with absolute media path at database'''

        return '/'.join(url.split('/')[2:])

    def parse_rows(self, structure_instance, rows):

        for row in rows:
            row_data = dict()
            row_id = int(row.attrib['id'])
            row_data['structure'] = structure_instance

            row_data['parent'] = row.find('parent').text
            if row_data['parent']:
                try:
                    row_data['parent'] = StructureRow.objects.get(external_id=int(row_data['parent']))
                except StructureRow.DoesNotExist:
                    continue

            row_data['title'] = row.find('title').text
            row_data['label'] = row.find('label').text
            row_data['entry'] = row.find('entry').text
            row_data['order'] = int(row.find('order').text)
            row_data['date_start'] = row.find('date_start').text
            row_data['date_end'] = row.find('date_end').text

            allowed_users = []
            for xml_user in row.findall('user'):
                username = xml_user.find('username').text
                email = xml_user.find('email').text or 'default@default.com'
                password = xml_user.find('password').text

                user_instance, user_created = User.objects.get_or_create(username=username, defaults={'email': email, 'password': password})
                if not user_created:
                    user_instance.email = email
                    user_instance.password = password

                allowed_users.append(user_instance)

            row_data['mediafile'] = row.find('mediafile')
            media_id = row_data['mediafile'].attrib.get('id', None)
            if media_id:
                get_mdata = lambda key: row_data['mediafile'].attrib.get(key, '')

                media_data = dict()
                media_data['title'] = get_mdata('title')
                media_data['label'] = get_mdata('label')
                media_data['media_type'] = get_mdata('media_type')
                media_data['created'] = get_mdata('created')
                media_data['path'] = self.fix_media_url(get_mdata('path'))
                media_data['video_image'] = self.fix_media_url(get_mdata('video_image'))
                media_data['duration'] = get_mdata('duration')
                

                media_instance, media_created = MediaFile.objects.get_or_create(external_id=int(media_id), defaults=media_data)
                if not media_created:
                    media_instance.title = media_data['title']
                    media_instance.label = media_data['label']
                    media_instance.media_type = media_data['media_type']
                    media_instance.path = media_data['path']
                    media_instance.video_image = media_data['video_image']
                    media_instance.save()

                row_data['mediafile'] = media_instance
            else:
                row_data['mediafile'] = None


            row_instance, row_created = StructureRow.objects.get_or_create(external_id=row_id, defaults=row_data)
            if not row_created:
                row_instance.title = row_data['title']
                row_instance.parent = row_data['parent']
                row_instance.label = row_data['label']
                row_instance.entry = row_data['entry']
                row_instance.order = row_data['order']
                row_instance.date_start = row_data['date_start']
                row_instance.date_end = row_data['date_end']
                row_instance.mediafile = row_data['mediafile']
                row_instance.duration = row_data['duration']
                row_instance.save()

            for u_instance in allowed_users:
                row_instance.users.add(u_instance)


            new_rows = row.findall('row')
            if new_rows:
                self.parse_rows(structure_instance, new_rows)


    def save(self):
        data = dict()
        structure_id = int(self.xml.find('id').text)
        data['name'] = self.xml.find('name').text

        skin_data = dict()
        skin = self.xml.find('skin')
        skin_external_id = int(skin.find('external_id').text)
        skin_data['title'] = skin.find('title').text
        skin_data['slug'] = skin.find('slug').text

        mediadatabase_data = dict()
        mediadatabase = self.xml.find('mediadatabase')
        mediadatabase_data['name'] = mediadatabase.attrib['name']
        mediadatabase_data['slug'] = mediadatabase.attrib['slug']

        skin_instance, skin_created = Skin.objects.get_or_create(external_id=skin_external_id, defaults=skin_data)
        if not skin_created:
            skin_instance.title = skin_data['title']
            skin_instance.slug = skin_data['slug']
            skin_instance.save()

        mediadatabase_instance, mediadatabase_created = MediaDatabase.objects.get_or_create(**mediadatabase_data)

        data['skin'] = skin_instance
        data['mediadatabase'] = mediadatabase_instance
        structure_instance, structure_created = Structure.objects.get_or_create(external_id=structure_id, defaults=data)
        if not structure_created:
            structure_instance.name = data['name']
            structure_instance.save()

        rows = self.xml.findall('row')
        self.parse_rows(structure_instance, rows)


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



VLC_BASE_COMMAND =  "cvlc --fullscreen                   \
                    --aspect 4:3                         \
                    --no-video-title-show                \
                    --random                             \
                    --loop                               \
                    --key-toggle-fullscreen=''           \
                    --global-key-toggle-fullscreen=''    \
                    --key-leave-fullscreen=''            \
                    --global-key-leave-fullscreen=''     \
                    --key-play-pause='p'                 \
                    --global-key-play-pause=''           \
                    --key-faster=''                      \
                    --global-key-faster=''               \
                    --key-slower=''                      \
                    --global-key-slower=''               \
                    --key-rate-normal=''                 \
                    --global-key-rate-normal=''          \
                    --key-rate-faster-fine=''            \
                    --global-key-rate-faster-fine=''     \
                    --key-rate-slower-fine=''            \
                    --global-key-rate-slower-fine=''     \
                    --key-next='n'                       \
                    --global-key-next=''                 \
                    --key-prev=''                        \
                    --global-key-prev=''                 \
                    --key-stop=''                        \
                    --global-key-stop=''                 \
                    --key-jump-extrashort=''             \
                    --global-key-jump-extrashort=''      \
                    --key-jump+extrashort=''             \
                    --global-key-jump+extrashort=''      \
                    --key-jump-short=''                  \
                    --global-key-jump-short=''           \
                    --key-jump+short=''                  \
                    --global-key-jump+short=''           \
                    --key-jump-medium=''                 \
                    --global-key-jump-medium=''          \
                    --key-jump+medium=''                 \
                    --global-key-jump+medium=''          \
                    --key-jump-long=''                   \
                    --global-key-jump-long=''            \
                    --key-jump+long=''                   \
                    --global-key-jump+long=''            \
                    --key-frame-next=''                  \
                    --global-key-frame-next=''           \
                    --key-quit='v'                       \
                    --global-key-quit='v'                \
                    --key-vol-up=''                      \
                    --global-key-vol-up=''               \
                    --key-vol-down=''                    \
                    --global-key-vol-down=''             \
                    --key-vol-mute=''                    \
                    --global-key-vol-mute=''             \
                    --key-audio-track=''                 \
                    --global-key-audio-track=''          \
                    --key-audiodevice-cycle=''           \
                    --global-key-audiodevice-cycle=''    \
                    --key-subtitle-track=''              \
                    --global-key-subtitle-track=''       \
                    --key-aspect-ratio=''                \
                    --global-key-aspect-ratio=''         \
                    --key-crop=''                        \
                    --global-key-crop=''                 \
                    --key-toggle-autoscale=''            \
                    --global-key-toggle-autoscale=''     \
                    --key-incr-scalefactor=''            \
                    --global-key-incr-scalefactor=''     \
                    --key-decr-scalefactor=''            \
                    --global-key-decr-scalefactor=''     \
                    --key-deinterlace=''                 \
                    --global-key-deinterlace=''          \
                    --key-wallpaper=''                   \
                    --global-key-wallpaper=''            \
                    --key-random=''                      \
                    --global-key-random=''               \
                    --key-loop=''                        \
                    --global-key-loop=''                 \
                    --play-and-exit"

