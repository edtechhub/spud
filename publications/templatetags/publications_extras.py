from django import template
from datetime import datetime

register = template.Library()

@register.filter("timestamp")
def timestamp(value):
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
