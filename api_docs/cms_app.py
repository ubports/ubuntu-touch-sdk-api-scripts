"""Application hooks for cmsplugin_zinnia"""
import warnings

from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

class ApidocsApphook(CMSApp):
    """
    Zinnia's Apphook
    """
    name = _('API Documentation')
    urls = ['api_docs.urls']

apphook_pool.register(ApidocsApphook)
