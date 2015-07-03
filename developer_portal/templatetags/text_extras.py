from django import template
import re
import random
register = template.Library()

@register.filter
def index(List, item):
    return list(List).index(item)+1

@register.filter
def html_links(text):
    # url to link
    urls = re.compile(r"((https?):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", re.MULTILINE|re.UNICODE)
    text = urls.sub(r'<a href="\1" target="_blank">\1</a>', text)
    # email to mailto
    urls = re.compile(r"([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)", re.MULTILINE|re.UNICODE)
    text = urls.sub(r'<a href="mailto:\1">\1</a>', text)
    return text

@register.filter
def randint(mini, maxi):
    return random.randint(mini, maxi)

@register.filter
def string(integer):
    return str(integer)
