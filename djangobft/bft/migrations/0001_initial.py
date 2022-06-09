# encoding: utf-8
from django.db import models
from south.db import db
from south.v2 import SchemaMigration
import datetime

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Submission'
        db.create_table('bft_submission', ( #@UndefinedVariable
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('email_address', self.gf('django.db.models.fields.EmailField')(max_length=255)),
            ('anumbers', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('submit_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, blank=True)),
            ('submit_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('is_archived', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('email_sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('browser_meta', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('bft', ['Submission']) #@UndefinedVariable

        # Adding model 'Email'
        db.create_table('bft_email', ( #@UndefinedVariable
            ('submission_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['bft.Submission'], unique=True, primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('recipients', self.gf('django.db.models.fields.TextField')()),
            ('message', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('bft', ['Email']) #@UndefinedVariable

        # Adding model 'File'
        db.create_table('bft_file', ( #@UndefinedVariable
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bft.Submission'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('file_upload', self.gf('django.db.models.fields.files.FileField')(max_length=500)),
            ('file_size', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=3)),
        ))
        db.send_create_signal('bft', ['File']) #@UndefinedVariable

        # Adding model 'FileArchive'
        db.create_table('bft_filearchive', ( #@UndefinedVariable
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bft.Submission'])),
            ('file_upload', self.gf('django.db.models.fields.FilePathField')(max_length=100)),
            ('submit_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('delete_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('bft', ['FileArchive']) #@UndefinedVariable


    def backwards(self, orm):
        
        # Deleting model 'Submission'
        db.delete_table('bft_submission') #@UndefinedVariable

        # Deleting model 'Email'
        db.delete_table('bft_email') #@UndefinedVariable

        # Deleting model 'File'
        db.delete_table('bft_file') #@UndefinedVariable

        # Deleting model 'FileArchive'
        db.delete_table('bft_filearchive') #@UndefinedVariable


    models = {
        'bft.email': {
            'Meta': {'object_name': 'Email', '_ormbases': ['bft.Submission']},
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'recipients': ('django.db.models.fields.TextField', [], {}),
            'submission_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['bft.Submission']", 'unique': 'True', 'primary_key': 'True'})
        },
        'bft.file': {
            'Meta': {'object_name': 'File'},
            'file_size': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '3'}),
            'file_upload': ('django.db.models.fields.files.FileField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bft.Submission']"})
        },
        'bft.filearchive': {
            'Meta': {'object_name': 'FileArchive'},
            'delete_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file_upload': ('django.db.models.fields.FilePathField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bft.Submission']"}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {})
        },
        'bft.submission': {
            'Meta': {'object_name': 'Submission'},
            'anumbers': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'browser_meta': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            'email_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'submit_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['bft']
