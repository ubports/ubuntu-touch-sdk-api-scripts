"""Views for Zinnia archives"""
import datetime

from django.utils import timezone
from zinnia.views.archives import EntryDay
from zinnia.views.archives import EntryWeek
from zinnia.views.archives import EntryYear
from zinnia.views.archives import EntryMonth
from zinnia.views.archives import EntryToday
from zinnia.views.archives import EntryIndex

from cms.utils import get_language_code
from django.utils.translation import get_language

class MultiLangMixin:
    """
    Uses the request to determine the current language and filters
    entry results to a category of the same name
    """
    def set_language(self, request):
        current_language = request.REQUEST.get('language', None)
        if current_language:
            current_language = get_language_code(current_language)
        if current_language is None:
            current_language = get_language_code(getattr(request, 'LANGUAGE_CODE', None))
            if current_language:
                current_language = get_language_code(current_language)
        if current_language is None:
            current_language = get_language_code(get_language())
        self.language = current_language

class MultiLangEntryIndex(MultiLangMixin, EntryIndex):
    def get(self, request, *args, **kwargs):
        self.set_language(request)
        return super(MultiLangEntryIndex, self).get(request, *args, **kwargs)

    def get_dated_queryset(self, ordering=None, **lookup):
        if ordering:
            return super(MultiLangEntryIndex, self).get_dated_queryset(**lookup).filter(categories__slug=self.language).order_by(ordering)
        return super(MultiLangEntryIndex, self).get_dated_queryset(**lookup).filter(categories__slug=self.language)

class MultiLangEntryYear(MultiLangMixin, EntryYear):
    def get(self, request, *args, **kwargs):
        self.set_language(request)
        return super(MultiLangEntryYear, self).get(request, *args, **kwargs)

    def get_dated_queryset(self, ordering=None, **lookup):
        if ordering:
            return super(MultiLangEntryYear, self).get_dated_queryset(**lookup).filter(categories__slug=self.language).order_by(ordering)
        return super(MultiLangEntryYear, self).get_dated_queryset(**lookup).filter(categories__slug=self.language)

class MultiLangEntryMonth(MultiLangMixin, EntryMonth):
    def get(self, request, *args, **kwargs):
        self.set_language(request)
        return super(MultiLangEntryMonth, self).get(request, *args, **kwargs)

    def get_dated_queryset(self, ordering=None, **lookup):
        if ordering:
            return super(MultiLangEntryMonth, self).get_dated_queryset(**lookup).filter(categories__slug=self.language).order_by(ordering)
        return super(MultiLangEntryMonth, self).get_dated_queryset(**lookup).filter(categories__slug=self.language)

class MultiLangEntryWeek(MultiLangMixin, EntryWeek):
    def get(self, request, *args, **kwargs):
        self.set_language(request)
        return super(MultiLangEntryWeek, self).get(request, *args, **kwargs)

    def get_dated_queryset(self, ordering=None, **lookup):
        if ordering:
            return super(MultiLangEntryWeek, self).get_dated_queryset(**lookup).filter(categories__slug=self.language).order_by(ordering)
        return super(MultiLangEntryWeek, self).get_dated_queryset(**lookup).filter(categories__slug=self.language)

class MultiLangEntryDay(MultiLangMixin, EntryDay):
    def get(self, request, *args, **kwargs):
        self.set_language(request)
        return super(MultiLangEntryDay, self).get(request, *args, **kwargs)

    def get_dated_queryset(self, ordering=None, **lookup):
        if ordering:
            return super(MultiLangEntryDay, self).get_dated_queryset(**lookup).filter(categories__slug=self.language).order_by(ordering)
        return super(MultiLangEntryDay, self).get_dated_queryset(**lookup).filter(categories__slug=self.language)

class MultiLangEntryToday(MultiLangMixin, EntryToday):
    def get(self, request, *args, **kwargs):
        self.set_language(request)
        return super(MultiLangEntryToday, self).get(request, *args, **kwargs)

    def get_dated_queryset(self, ordering=None, **lookup):
        if ordering:
            return super(MultiLangEntryToday, self).get_dated_queryset(**lookup).filter(categories__slug=self.language).order_by(ordering)
        return super(MultiLangEntryToday, self).get_dated_queryset(**lookup).filter(categories__slug=self.language)
