from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from djangocms_text_ckeditor.cms_plugins import TextPlugin

from .models import RawHtml

class RawHtmlPlugin(TextPlugin):
    model = RawHtml
    name = _("Raw HTML")
    render_template = "developer_portal/raw.html"
    
plugin_pool.register_plugin(RawHtmlPlugin)
