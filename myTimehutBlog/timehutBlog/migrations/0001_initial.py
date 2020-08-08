# Generated by Django 2.0.6 on 2018-08-04 12:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PeekabooCollection',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('baby_id', models.CharField(blank=True, max_length=32, null=True)),
                ('created_at', models.IntegerField(blank=True, null=True)),
                ('updated_at', models.IntegerField(blank=True, null=True)),
                ('months', models.IntegerField(blank=True, null=True)),
                ('days', models.IntegerField(blank=True, null=True)),
                ('content_type', models.SmallIntegerField(blank=True, null=True)),
                ('caption', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'peekaboo_collection',
                'ordering': ('-created_at',),
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='PeekabooMoment',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('baby_id', models.CharField(blank=True, max_length=32, null=True)),
                ('created_at', models.IntegerField(blank=True, null=True)),
                ('updated_at', models.IntegerField(blank=True, null=True)),
                ('content_type', models.SmallIntegerField(blank=True, null=True)),
                ('content', models.TextField(blank=True, null=True)),
                ('src_url', models.CharField(blank=True, max_length=512, null=True)),
                ('months', models.IntegerField(blank=True, null=True)),
                ('days', models.IntegerField(blank=True, null=True)),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='event_id', to='timehutBlog.PeekabooCollection')),
            ],
            options={
                'db_table': 'peekaboo_moment',
                'ordering': ('-created_at',),
                'managed': True,
            },
        ),
    ]