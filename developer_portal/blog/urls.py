# Override Zinnia's default urlconf to filter listings by language/category

"""Urls for the Zinnia archives"""
from django.conf.urls import url
from django.conf.urls import include
from django.conf.urls import patterns

from zinnia.urls import _
from developer_portal.blog.views import MultiLangEntryDay
from developer_portal.blog.views import MultiLangEntryWeek
from developer_portal.blog.views import MultiLangEntryYear
from developer_portal.blog.views import MultiLangEntryMonth
from developer_portal.blog.views import MultiLangEntryToday
from developer_portal.blog.views import MultiLangEntryIndex

urlpatterns = patterns(
    '',
    url(_(r'^feeds/'), include('zinnia.urls.feeds')),
    url(_(r'^tags/'), include('zinnia.urls.tags')),
    url(_(r'^authors/'), include('zinnia.urls.authors')),
    url(_(r'^categories/'), include('zinnia.urls.categories')),
    url(_(r'^search/'), include('zinnia.urls.search')),
    url(_(r'^random/'), include('zinnia.urls.random')),
    url(_(r'^sitemap/'), include('zinnia.urls.sitemap')),
    url(_(r'^trackback/'), include('zinnia.urls.trackback')),
    url(_(r'^comments/'), include('zinnia.urls.comments')),
    url(r'^', include('zinnia.urls.entries')),

    url(r'^$',
        MultiLangEntryIndex.as_view(),
        name='entry_archive_index'),
    url(_(r'^page/(?P<page>\d+)/$'),
        MultiLangEntryIndex.as_view(),
        name='entry_archive_index_paginated'),

    url(r'^(?P<year>\d{4})/$',
        MultiLangEntryYear.as_view(),
        name='entry_archive_year'),
    url(_(r'^(?P<year>\d{4})/page/(?P<page>\d+)/$'),
        MultiLangEntryYear.as_view(),
        name='entry_archive_year_paginated'),

    url(_(r'^(?P<year>\d{4})/week/(?P<week>\d+)/$'),
        MultiLangEntryWeek.as_view(),
        name='entry_archive_week'),
    url(_(r'^(?P<year>\d{4})/week/(?P<week>\d+)/page/(?P<page>\d+)/$'),
        MultiLangEntryWeek.as_view(),
        name='entry_archive_week_paginated'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
        MultiLangEntryMonth.as_view(),
        name='entry_archive_month'),
    url(_(r'^(?P<year>\d{4})/(?P<month>\d{2})/page/(?P<page>\d+)/$'),
        MultiLangEntryMonth.as_view(),
        name='entry_archive_month_paginated'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
        MultiLangEntryDay.as_view(),
        name='entry_archive_day'),
    url(_(r'^(?P<year>\d{4})/(?P<month>\d{2})/'
          '(?P<day>\d{2})/page/(?P<page>\d+)/$'),
        MultiLangEntryDay.as_view(),
        name='entry_archive_day_paginated'),

    url(_(r'^today/$'),
        MultiLangEntryToday.as_view(),
        name='entry_archive_today'),
    url(_(r'^today/page/(?P<page>\d+)/$'),
        MultiLangEntryToday.as_view(),
        name='entry_archive_today_paginated'),

    url(r'^', include('zinnia.urls.shortlink')),
    url(r'^', include('zinnia.urls.quick_entry')),
    url(r'^', include('zinnia.urls.capabilities')),
)

