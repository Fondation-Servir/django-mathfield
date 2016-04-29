from __future__ import unicode_literals
from django import forms
from django.utils.safestring import mark_safe
from mathfield.api import store_math
from django.conf import settings
import textwrap
import json
import cgi

try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str,bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring

class MathFieldWidget(forms.Textarea):

    def render(self, name, value, attrs=None):
        output = super(MathFieldWidget, self).render(name, value, attrs)
        output = '<div id="{0}-container"><span>{1}</span></div>'.format(
            attrs['id'], output)

        if value:
            if isinstance(value, basestring):
           	    try:
           	    	value = dict(json.loads(value))
           	    except (ValueError, TypeError):
           	    	# the value was stored as just a string. Try to compile it to
           	    	# LaTeX and return a dictionary, or raise a NodeError
           	    	value = store_math(value)

            if isinstance(value, dict):
            	raw = value['raw'] if 'raw' in value else ''
            	html = value['html'] if 'html' in value else ''
            	html = html.replace('"', '\\"').replace("'", "\\'")
            	raw = raw.replace('\n', '\\n').replace("\n", "\\n")
            	html = html.replace('\n', '<br />').replace("\n", "<br />")
            elif isinstance(value, basestring):
            	raw = value
            	html = ''
            	raw = cgi.escape(raw.replace('\\', '\\\\'))
        else:
            raw = html = ''

        if hasattr(settings, 'STATIC_URL'):
            static_url = getattr(settings, 'STATIC_URL', {})
        else:
            static_url = '/static/'
        output += textwrap.dedent("""
            <link rel="stylesheet" type="text/css"
                href="{static}mathfield/css/mathfield.css"/>
            <script type="text/javascript"
                src="{static}mathfield/js/mathfield.min.js"></script>
            <script type="text/javascript">
                renderMathFieldForm("{id}", "{raw}", "{html}");
            </script>
        """.format(static=static_url, id=attrs['id'], raw=raw, html=html))

        return mark_safe(output)
