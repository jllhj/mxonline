# Generated by Django 2.0.2 on 2019-03-15 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='courseorg',
            name='course_nums',
        ),
        migrations.RemoveField(
            model_name='courseorg',
            name='students',
        ),
        migrations.RemoveField(
            model_name='courseorg',
            name='tag',
        ),
        migrations.AlterField(
            model_name='courseorg',
            name='category',
            field=models.CharField(choices=[('pxjg', '培训机构'), ('gx', '高校'), ('gr', '个人')], default='pxjg', max_length=20, verbose_name='机构类别'),
        ),
        migrations.AlterField(
            model_name='courseorg',
            name='image',
            field=models.ImageField(upload_to='org/%Y%m', verbose_name='logo'),
        ),
    ]
