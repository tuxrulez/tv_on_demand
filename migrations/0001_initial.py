# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Skin'
        db.create_table('tv_on_demand_skin', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=45)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=45, db_index=True)),
        ))
        db.send_create_signal('tv_on_demand', ['Skin'])

        # Adding model 'Structure'
        db.create_table('tv_on_demand_structure', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('skin', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tv_on_demand.Skin'])),
            ('mediadatabase', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mediafiles.MediaDatabase'])),
        ))
        db.send_create_signal('tv_on_demand', ['Structure'])

        # Adding model 'StructureRow'
        db.create_table('tv_on_demand_structurerow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tv_on_demand.Structure'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['tv_on_demand.StructureRow'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('label', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('mediafile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mediafiles.MediaFile'], null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('tv_on_demand', ['StructureRow'])


    def backwards(self, orm):
        
        # Deleting model 'Skin'
        db.delete_table('tv_on_demand_skin')

        # Deleting model 'Structure'
        db.delete_table('tv_on_demand_structure')

        # Deleting model 'StructureRow'
        db.delete_table('tv_on_demand_structurerow')


    models = {
        'mediafiles.genre': {
            'Meta': {'object_name': 'Genre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '45'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '45', 'db_index': 'True'})
        },
        'mediafiles.mediadatabase': {
            'Meta': {'object_name': 'MediaDatabase'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'mediafiles.mediafile': {
            'Meta': {'object_name': 'MediaFile'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mediafiles.Genre']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'media_database': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mediafiles.MediaDatabase']"}),
            'media_type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'path': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'video_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'tv_on_demand.skin': {
            'Meta': {'object_name': 'Skin'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '45', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '45'})
        },
        'tv_on_demand.structure': {
            'Meta': {'object_name': 'Structure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mediadatabase': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mediafiles.MediaDatabase']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'skin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tv_on_demand.Skin']"})
        },
        'tv_on_demand.structurerow': {
            'Meta': {'object_name': 'StructureRow'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'mediafile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mediafiles.MediaFile']", 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['tv_on_demand.StructureRow']"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tv_on_demand.Structure']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['tv_on_demand']
