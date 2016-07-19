from django.db import models

# Create your models here.

class PathMatchRedirect(models.Model):
    
    match = models.CharField(max_length=256, help_text="Path prefix to match for this redirect")
    replace = models.CharField(max_length=256, help_text="Replacement path")
    preserve_extra = models.BooleanField(default=True, help_text="Should any part of the path after what was matched be appended to the replacement path?")
    precedence = models.IntegerField(help_text="Auto-calculated, leave blank", blank=True)
    
    def save(self, *args, **kwargs):
        # We'll want to check more specific URL paths first, which we 
        # can do if we reverse sort by length
        self.precedence = len(self.match)
        super(PathMatchRedirect, self).save()
        
    def __unicode__(self):
        return self.match
