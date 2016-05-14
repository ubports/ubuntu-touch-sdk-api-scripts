from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from .models import GadgetSnap


class GadgetSnapListPluginLarge(CMSPluginBase):
    # Keeping the name short to be able to differentiate them
    # in the editor dropdown
    name = _("Snap list - Gadget")
    render_template = "gadget_snap_list.html"
    text_enabled = True

    def render(self, context, instance, placeholder):
        context.update({
            'gadget_snap_list': GadgetSnap.objects.order_by('-release'),
        })
        return context

plugin_pool.register_plugin(GadgetSnapListPluginLarge)


class GadgetSnapListPluginSmall(CMSPluginBase):
    # Keeping the name short to be able to differentiate them
    # in the editor dropdown
    name = _("Snap shortlist - Gadget")
    render_template = "gadget_snap_shortlist.html"
    text_enabled = True

    def render(self, context, instance, placeholder):
        context.update({
            'gadget_snap_list': GadgetSnap.objects.order_by('-release'),
        })
        return context

plugin_pool.register_plugin(GadgetSnapListPluginSmall)
