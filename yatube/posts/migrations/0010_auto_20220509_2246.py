# Generated by Django 2.2.6 on 2022-05-09 22:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_auto_20220430_1127'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'permissions': (('can_add_groups', 'group was added'),), 'verbose_name': 'Группа', 'verbose_name_plural': 'Группы'},
        ),
    ]
