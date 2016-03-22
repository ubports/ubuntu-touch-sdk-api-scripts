from django.db import models

# Create your models here.

class Topic(models.Model):
    
    name = models.CharField(max_length=64)
    slug = models.CharField(max_length=64)
    
    def __unicode__(self):
        return self.name

class Language(models.Model):

    topic = models.ForeignKey(Topic)
    name = models.CharField(max_length=64)
    slug = models.CharField(max_length=64)

    current_version = models.ForeignKey('Version', blank=True, null=True, related_name='current_for_lang')
    development_version = models.ForeignKey('Version', blank=True, null=True, related_name='development_for_lang')

    def __unicode__(self):
        return self.topic.name +' '+self.name
    
class Version(models.Model):
    
    language = models.ForeignKey(Language, null=True)
    name = models.CharField(max_length=64)
    slug = models.CharField(max_length=64)

    def import_from(self, target_version):
        for section in target_version.section_set.all():
            self.section_set.add(section.clone())
            
    def __unicode__(self):
        return self.language.topic.name +' '+self.language.name +' '+self.name


class Section(models.Model):

    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)
    topic_version = models.ForeignKey(Version)
    
    def __unicode__(self):
        return self.topic_version.language.topic.name +' '+ self.topic_version.language.name +' '+self.topic_version.name+', '+self.name

    def clone(self):
        new = Section(name=self.name, description=self.description, topic_version=self.topic_version)
        new.save()
        for namespace in self.namespace_set.all():
            new.namespace_set.add(namespace.clone(new))
            
        for element in self.element_set.all():
            if not element.namespace:
                element.section = new
                element.id = None
                element.save()
                new.element_set.add(element)

        for page in self.page_set.all():
            if not page.namespace:
                page.section = new
                page.id = None
                page.save()
                new.page_set.add(page)

        return new
        
    @property
    def topic(self):
        return self.topic_version.topic
        
    def has_namespaces(self):
        return self.namespace_set.count() > 0
    
    def has_free_elements(self):
        return self.element_set.filter(namespace=None).count() > 0
    
    def free_element_set(self):
        return self.element_set.filter(namespace=None)

    def has_free_pages(self):
        return self.page_set.filter(namespace=None).count() > 0
    
    def free_page_set(self):
        return self.page_set.filter(namespace=None)

class Namespace(models.Model):

    platform_section = models.ForeignKey(Section)
    name = models.CharField(max_length=64)
    display_name = models.CharField(max_length=64, blank=True, default='')

    data = models.TextField(blank=True, default='')
    source_file = models.CharField(max_length=128, blank=True, null=True)
    source_format = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return u'%s' % self.name
        
    def clone(self, new_section):
        new = Namespace(name=self.name, display_name=self.display_name, data=self.data, source_file=self.source_file, source_format=self.source_format, platform_section=new_section)
        new.save()

        for element in self.element_set.all():
            element.section = new_section
            element.namespace = new
            element.id = None
            element.save()
            new.element_set.add(element)

        for page in self.page_set.all():
            page.section = new_section
            page.namespace = new
            page.id = None
            page.save()
            new.page_set.add(page)

        return new

    @property
    def display(self):
        if self.display_name:
            return self.display_name
        else:
            return self.name


class Element(models.Model):
    'Displayable API Element'

    name = models.CharField(max_length=64)
    description= models.CharField(max_length=256, blank=True, default='')
    namespace = models.ForeignKey(Namespace, blank=True, null=True)

    section = models.ForeignKey(Section)
    fullname = models.CharField(max_length=128)
    keywords = models.CharField(max_length=256, blank=True, default='')
    data = models.TextField(blank=True, default='')

    source_file = models.CharField(max_length=128, blank=True, null=True)
    source_format = models.CharField(max_length=32, blank=True, null=True)
    
    class Meta:
        verbose_name = "Rendered Element"
        verbose_name_plural = "Rendered Elements"
        ordering = ('name',)

    def __unicode__(self):
        return u'%s' % self.fullname

    @property
    def platform_section(self):
        return self.section


class Page(models.Model):
    'Displayable Page of non-Element content'

    slug = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    description= models.CharField(max_length=256, blank=True, default='')
    namespace = models.ForeignKey(Namespace, blank=True, null=True)

    section = models.ForeignKey(Section)
    fullname = models.CharField(max_length=128)
    keywords = models.CharField(max_length=256, blank=True, default='')
    data = models.TextField(blank=True, default='')

    source_file = models.CharField(max_length=128, blank=True, null=True)
    source_format = models.CharField(max_length=32, blank=True, null=True)
    order_index = models.PositiveIntegerField(blank=True, null=False, default=0)
    
    class Meta:
        verbose_name = "Rendered Page"
        verbose_name_plural = "Rendered Pages"
        ordering = ('order_index',)

    def __unicode__(self):
        return u'%s' % self.fullname

