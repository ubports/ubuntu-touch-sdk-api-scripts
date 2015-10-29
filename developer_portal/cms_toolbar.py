from cms.extensions.toolbar import ExtensionToolbar
from cms.toolbar_pool import toolbar_pool
from django.utils.translation import get_language_from_request, ugettext_lazy as _
from .models import SEOExtension

from django.core.urlresolvers import NoReverseMatch
from cms.utils.urlutils import admin_reverse

@toolbar_pool.register
class SEOExtensionToolbar(ExtensionToolbar):
    # setup the extension toolbar with permissions and sanity checks
    model = SEOExtension

    def populate(self):
        # setup the extension toolbar with permissions and sanity checks
        current_page_menu = self._setup_extension_toolbar()
        # if it's all ok
        if current_page_menu and self.toolbar.edit_mode:
            # retrieves the instances of the current title extension (if any) and the toolbar item url
            lang = get_language_from_request(self.request, check_path=True)
            print lang
            urls = self.get_title_extension_admin(lang)
            print urls
            # cycle through the title list
            for title_extension, url in urls:
                # adds toolbar items
                current_page_menu.add_modal_item('SEO Keywords', url=url, disabled=not self.toolbar.edit_mode)

    def get_title_extension_admin(self, language=None):
        """
        Get the admin urls for the title extensions menu items, depending on whether a TitleExtension instance exists
        for each Title in the current page.
        A single language can be passed to only work on a single title.

        Return a list of tuples of the title extension and the url; the extension is None if no instance exists,
        the url is None is no admin is registered for the extension.
        """
        page = self._get_page()
        urls = []
        if language:
            titles = page.get_title_obj(language),
        else:
            titles = page.title_set.all()
        # Titles
        for title in titles:
            try:
                title_extension = self.model.objects.get(extended_object_id=title.pk)
            except self.model.DoesNotExist:
                title_extension = None
            try:
                if title_extension:
                    admin_url = admin_reverse(
                        '%s_%s_change' % (self.model._meta.app_label, self.model._meta.model_name),
                        args=(title_extension.pk,))
                else:
                    admin_url = "%s?extended_object=%s" % (
                        admin_reverse('%s_%s_add' % (self.model._meta.app_label, self.model._meta.model_name)),
                        title.pk)
            except NoReverseMatch:  # pragma: no cover
                admin_url = None
            if admin_url:
                urls.append((title_extension, admin_url))
        return urls
