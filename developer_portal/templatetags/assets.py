from django import template
from django.template.base import Node
from django.utils.encoding import iri_to_uri
from django.utils.six.moves.urllib.parse import urljoin
from django.templatetags.static import PrefixNode

register = template.Library()

# Copied with modifications from django.templatetags.static
class AssetNode(Node):
    def __init__(self, varname=None, path=None):
        if path is None:
            raise template.TemplateSyntaxError(
                "Asset template nodes must be given a path to return.")
        self.path = path
        self.varname = varname

    def url(self, context):
        path = self.path.resolve(context)
        return self.handle_simple(path)

    def render(self, context):
        url = self.url(context)
        if self.varname is None:
            return url
        context[self.varname] = url
        return ''

    @classmethod
    def handle_simple(cls, path):
        return urljoin(PrefixNode.handle_simple("ASSETS_URL"), path)

    @classmethod
    def handle_token(cls, parser, token):
        """
        Class method to parse prefix node and return a Node.
        """
        bits = token.split_contents()

        if len(bits) < 2:
            raise template.TemplateSyntaxError(
                "'%s' takes at least one argument (path to file)" % bits[0])

        path = parser.compile_filter(bits[1])

        if len(bits) >= 2 and bits[-2] == 'as':
            varname = bits[3]
        else:
            varname = None

        return cls(varname, path)

# Copied with modifications from django.contrib.staticfiles.templatetags.staticfiles and
@register.tag('assets')
def do_assets(parser, token):
    """
    A template tag that returns the URL to a file
    using ASSETS_URL prefix

    Usage::

        {% assets path [as varname] %}

    Examples::

        {% assets "myapp/css/base.css" %}
        {% assets variable_with_path %}
        {% assets "myapp/css/base.css" as admin_base_css %}
        {% assets variable_with_path as varname %}

    """
    return AssetNode.handle_token(parser, token)



