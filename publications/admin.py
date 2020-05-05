from django.contrib import admin

from .models import Publication

class PublicationAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'authors', 'year', 'keywords', 'abstract')
	search_fields = ('title', 'authors', 'year', 'keywords', 'abstract')

	# def get_search_results(self, request, queryset, search_term):
	# 	import pdb; pdb.set_trace();
	# 	queryset, use_distinct = super(PublicationAdmin, self).get_search_results(request, queryset, search_term)
	# 	try:
	# 		search_term_as_int = int(search_term)
	# 		queryset |= self.model.objects.filter(age=search_term_as_int)
	# 	except:
	# 		pass
	# 	return queryset, use_distinct

admin.site.register(Publication, PublicationAdmin)
