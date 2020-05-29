from django import template
from django.utils.safestring import mark_safe
from django.conf import settings
import re

register = template.Library()


@register.filter('replace_highlighted')
def replace_highlighted(text):
	for (_key, _values) in settings.KEYWORDS.items():
		keywords_set = set(_values)
		for _value in keywords_set:

			if _value.isupper():
				text = re.sub(_value, "<span class='mark%s'>%s</span>" % (_key, _value), text)
			else:
				text = re.sub(_value, "<span class='mark%s'>%s</span>" % (_key, _value), text, flags=re.I)

	return mark_safe(text)
