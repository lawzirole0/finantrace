from django.db import migrations
from django.conf import settings


def update_site_domain(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    domain = getattr(settings, 'SITE_DOMAIN', None)
    if not domain:
        hosts = getattr(settings, 'ALLOWED_HOSTS', [])
        domain = next((h for h in hosts if h != 'localhost' and not h.startswith('.')), 'finantrace.onrender.com')
    name = getattr(settings, 'SITE_NAME', 'finanTrace')
    Site.objects.update_or_create(id=1, defaults={'domain': domain, 'name': name})


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_userprofile_profession_and_more'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(update_site_domain, migrations.RunPython.noop),
    ]
