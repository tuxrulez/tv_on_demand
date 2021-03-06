# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Structure.password'
        db.add_column('tv_on_demand_structure', 'password', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Structure.password'
        db.delete_column('tv_on_demand_structure', 'password')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'clients.chain': {
            'Meta': {'object_name': 'Chain'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'})
        },
        'clients.store': {
            'Meta': {'object_name': 'Store'},
            'chain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clients.Chain']"}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['states.City']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'medialog': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['mediafiles.MediaLog']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['states.State']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
            'date_end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_start': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'days_of_week': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mediafiles.Genre']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'media_database': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mediafiles.MediaDatabase']"}),
            'media_type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'modified': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'new': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'path': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'time_end': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'time_start': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'video_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'mediafiles.medialog': {
            'Meta': {'object_name': 'MediaLog'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_view': ('django.db.models.fields.DateTimeField', [], {}),
            'mediafile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'medialogs'", 'to': "orm['mediafiles.MediaFile']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'medialogs'", 'null': 'True', 'to': "orm['auth.User']"}),
            'views_number': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'states.city': {
            'Meta': {'ordering': "['name']", 'object_name': 'City'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['states.State']"})
        },
        'states.state': {
            'Meta': {'ordering': "['name']", 'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'uf': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'tv_on_demand.skin': {
            'Meta': {'object_name': 'Skin'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '45', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '45'})
        },
        'tv_on_demand.structure': {
            'Meta': {'object_name': 'Structure'},
            'chain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clients.Chain']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mediadatabase': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mediafiles.MediaDatabase']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'password': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'skin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tv_on_demand.Skin']"}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clients.Store']", 'null': 'True', 'blank': 'True'})
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
