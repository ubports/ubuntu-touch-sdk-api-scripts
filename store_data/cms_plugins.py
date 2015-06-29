from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from .models import GadgetSnap


class GadgetSnapListPlugin(CMSPluginBase):
    model = GadgetSnap
    name = _("Gadget Snap List Plugin")
    render_template = "gadget_snap_list.html"

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        return context

plugin_pool.register_plugin(GadgetSnapListPlugin)
