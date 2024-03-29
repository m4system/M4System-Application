# Generated by Django 3.0.6 on 2020-05-29 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ModbusSourcePlugin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(blank=True, help_text='Internal name, leave empty to autopopulate.', max_length=64, unique=True, verbose_name='Name')),
                ('title', models.CharField(help_text='Verbose name for display purposes', max_length=256, verbose_name='Title')),
                ('start', models.CharField(help_text='The first register where we will start polling.', max_length=4096, verbose_name='Start Register')),
                ('count', models.CharField(help_text='This should match your data type.', max_length=4096, verbose_name='Amount of registers to poll sequentially.')),
                ('remote_type', models.CharField(choices=[('int16', 'Integer'), ('uint16', 'Unsigned Integer'), ('float', 'Float')], default='int16', help_text='Select the data format which matches the documentation of the device you are polling.', max_length=32, verbose_name='Remote Data Type')),
                ('byte_endian', models.CharField(choices=[('little', 'Little Endian'), ('big', 'Big Endian')], default='little', help_text='Little Endian is least significant bit first.', max_length=8, verbose_name='Byte Endian')),
                ('word_endian', models.CharField(choices=[('little', 'Little Endian'), ('big', 'Big Endian')], default='little', help_text='When there are more than 1 count (i.e. data types bigger than 16bit), this decides the order they are processed.', max_length=8, verbose_name='Word Endian')),
            ],
            options={
                'verbose_name': 'Modbus Source',
                'verbose_name_plural': 'Modbus Sources',
            },
        ),
    ]
