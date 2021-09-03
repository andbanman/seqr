# Generated by Django 3.1.13 on 2021-08-26 15:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('seqr', '0027_family_pedigree_dataset'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='analysis_status_last_modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='family',
            name='analysis_status_last_modified_date',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
    ]