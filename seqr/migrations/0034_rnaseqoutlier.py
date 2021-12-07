# Generated by Django 3.1.13 on 2021-12-06 21:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seqr', '0033_savedvariant_acmg_classification'),
    ]

    operations = [
        migrations.CreateModel(
            name='RnaSeqOutlier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gene_id', models.CharField(max_length=20)),
                ('p_value', models.FloatField()),
                ('p_adjust', models.FloatField()),
                ('z_score', models.FloatField()),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqr.sample')),
            ],
            options={
                'unique_together': {('sample', 'gene_id')},
            },
        ),
    ]