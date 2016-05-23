from optparse import make_option

from django.core.management.base import BaseCommand

from cms.models import Page


def find_pages_without_publisher_draft():
    return [p for p in Page.objects.all()
            if not hasattr(p, 'publisher_draft')]


def find_duplicates_pages():
    urls = [p.get_absolute_url() for p in Page.objects.all()]
    return [p for p in Page.objects.all()
            if urls.count(p.get_absolute_url()) == 2]


def print_pages(pages):
    for p in pages:
        print('{} ({})'.format
              (p.get_absolute_url(),
               'Draft' if p.publisher_is_draft else 'Public'))


def delete_pages(pages):
    for p in pages:
        print('Deleting page: {} ({})'.format
              (p.get_absolute_url(),
               'Draft' if p.publisher_is_draft else 'Public'))
        p.delete()


class Command(BaseCommand):
    help = "Make sure the CMS database is consistent."

    option_list = BaseCommand.option_list + (
        make_option(
            '--delete', action='store_true', dest='delete',
            default=True, help='Delete broken and inconsistent entries.'),
    )

    def handle(self, *args, **options):
        pages = find_pages_without_publisher_draft()
        print('Pages without .publisher_draft: {}'.format(len(pages)))
        if pages:
            if options['delete']:
                print_pages(pages)
            else:
                delete_pages(pages)

        pages = find_duplicates_pages()
        print('Duplicate pages: {}'.format(len(pages)))
        if pages:
            print_pages(pages)
            if options['delete']:
                print('Please remove them manually.')

        if not options['delete']:
            print('If you want any inconsistencies fixed, please re-run this '
                  'command with the --delete option.')
