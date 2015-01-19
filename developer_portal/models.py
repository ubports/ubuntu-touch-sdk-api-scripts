
from cms.models import CMSPlugin
from djangocms_text_ckeditor.html import extract_images
from djangocms_text_ckeditor.models import AbstractText

class RawHtml(AbstractText):
    
    class Meta:
        abstract = False

    def save(self, *args, **kwargs):
        body = self.body
        body = extract_images(body, self)
        self.body = body
        AbstractText.save(self, *args, **kwargs)
