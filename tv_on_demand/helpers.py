# -*- coding:utf-8 -*-

import os
from datetime import date
from StringIO import StringIO
from xml.etree import cElementTree as ElementTree
from elementtree.ElementTree import parse
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from mediafiles.models import MediaFile
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
            
            mf = row.mediafile
            if mf:
                try:
                    real_path = mf.path.url
                except ValueError:
                    real_path = ''
                
                ElementTree.SubElement(row_element, 'mediafile', id=str(mf.pk), media_type=mf.media_type,
                                       title=mf.title, label=mf.label, path=real_path, created=fix_date(mf.created))
            else:
                ElementTree.SubElement(row_element, 'mediafile')
                
            row_date_start = ElementTree.SubElement(row_element, 'date_start')
            row_date_start.text = fix_date(row.date_start)
            row_date_end = ElementTree.SubElement(row_element, 'date_end')
            row_date_end.text = fix_date(row.date_end)
            
            for user in row.users.all():
                row_user = ElementTree.SubElement(row_element, 'user', username=user.username, password=user.password,
                                                  email=user.email)
            
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
        structure_skin_css_style = ElementTree.SubElement(structure_skin, 'css_style')
        structure_skin_css_style.text = instance.skin.css_style.url
        structure_skin_external_id = ElementTree.SubElement(structure_skin, 'external_id')
        structure_skin_external_id.text = str(instance.skin.pk)

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
                                
                media_instance, media_created = MediaFile.objects.get_or_create(external_id=int(media_id), defaults=media_data)
                if media_created:
                    media_instance.title = media_data['title']
                    media_instance.label = media_data['label']
                    media_instance.media_type = media_data['media_type']
                    media_instance.path = media_data['path']
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
                row_instance.save()
                
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
        skin_data['css_style'] = self.fix_media_url(skin.find('css_style').text)
        
        skin_instance, skin_created = Skin.objects.get_or_create(external_id=skin_external_id, defaults=skin_data)
        if not skin_created:
            skin_instance.title = skin_data['title']
            skin_instance.slug = skin_data['slug']
            skin_instance.css_style = skin_data['css_style']
            skin_instance.save()
        
        data['skin'] = skin_instance
        structure_instance, structure_created = Structure.objects.get_or_create(external_id=structure_id, defaults=data)
        if not structure_created:
            structure_instance.name = data['name']
            structure_instance.save()
            
        rows = self.xml.findall('row')
        self.parse_rows(structure_instance, rows)
        
        
        
        
