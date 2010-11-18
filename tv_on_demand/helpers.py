# -*- coding:utf-8 -*-

import os
from datetime import date
from StringIO import StringIO
from xml.etree import cElementTree as ElementTree
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
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
                ElementTree.SubElement(parent_node, 'mediafile')
                
            row_date_start = ElementTree.SubElement(parent_node, 'date_start')
            row_date_start.text = fix_date(row.date_start)
            row_date_end = ElementTree.SubElement(parent_node, 'date_end')
            row_date_end.text = fix_date(row.date_end)
            
            for user in row.users.all():
                row_user = ElementTree.SubElement(parent_node, 'user', username=user.username, password=user.password,
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
        structure_template = ElementTree.SubElement(root, 'template')
        structure_template.text = instance.template.path

        row_qs = instance.structurerow_set.filter(parent=None)
        self._parse_rows(row_qs, root)
        
        return ElementTree.ElementTree(root)


    def save(self):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        xml_file = open(self.xml_path, 'wb')
        self._generate().write(xml_file)
        xml_file.close()
        
