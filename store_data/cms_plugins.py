from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from .models import GadgetSnap


class GadgetSnapListPlugin(CMSPluginBase):
    name = _("Gadget Snap List Plugin")
    render_template = "gadget_snap_list.html"

    def render(self, context, instance, placeholder):
        context.update({
            'gadget_snap_list': GadgetSnap.objects.all(),
        })
        return context

plugin_pool.register_plugin(GadgetSnapListPlugin)
