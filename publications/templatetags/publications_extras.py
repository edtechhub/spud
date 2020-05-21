from django import template
from datetime import datetime

register = template.Library()

@register.filter("timestamp")
def timestamp(value):
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@register.filter("check_availablity")
def check_availablity(value):
	if value.strip():
		return value
	else:
		return "(Not available.)"
