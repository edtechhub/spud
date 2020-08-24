from django import template
from datetime import datetime
from django.utils.safestring import mark_safe

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
	
@register.filter("make_links")
def make_links(value):
	value = value.split(",")
	text = ""
	for i in value:
		if i != "":
			text += "<a href='/detail/" + i.strip() + "/?auth=45728b6c-4227-11ea-905d-4bc10b2df14f' target='_blank'>" + i + "</a>; "
	return mark_safe(text)