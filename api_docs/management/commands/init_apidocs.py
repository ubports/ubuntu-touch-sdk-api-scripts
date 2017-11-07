from django.core.management.base import BaseCommand

from api_docs.models import Topic, Language, Version


class Command(BaseCommand):
    help = "Make sure the API database is set up properly."

    def handle(self, *args, **options):
        apps, _ = Topic.objects.update_or_create(name="apps", defaults={"slug": "apps"})
        autopilot, _ = Topic.objects.update_or_create(name="autopilot", defaults={"slug": "autopilot"})
        scopes, _ = Topic.objects.update_or_create(name="scopes", defaults={"slug": "scopes"})

        qml, _ = Language.objects.update_or_create(name="qml", defaults={'slug': 'qml', 'topic': apps})
        html, _ = Language.objects.update_or_create(name="html5", defaults={'slug': 'html5', 'topic': apps})
        python, _ = Language.objects.update_or_create(name="python", defaults={'slug': 'python', 'topic': autopilot})
        cpp, _ = Language.objects.update_or_create(name="cpp", defaults={'slug': 'cpp', 'topic': scopes})
        js, _ = Language.objects.update_or_create(name="js", defaults={'slug': 'js', 'topic': scopes})

        for lang in Language.objects.all():
            name = '{}-dev'.format(lang.name)
            version, _ = Version.objects.update_or_create(name=name, defaults={
                'slug': name,
                'language': lang,
            })

            lang.development_version = version
            lang.save()
