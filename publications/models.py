from django.db import models

from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

class Publication(models.Model):
	class Meta:
		db_table = 'publications'

	id = models.IntegerField(primary_key=True)
	title = models.TextField(blank = False)
	tak = models.TextField(blank = False)
	additionaltitles = models.TextField()
	authors = models.TextField(blank = False)
	year = models.TextField(blank = False)
	publicationtype = models.TextField()
	links = models.TextField()
	importedfrom = models.TextField()
	containername = models.TextField()
	doi = models.TextField()

	tsv = SearchVectorField(null=True)

	recordmetadata_zbuamajorversion = models.TextField()
	recordmetadata_dateretrieved = models.TextField()
	recordmetadata_dateconverted = models.TextField()
	recordmetadata_recordtype = models.TextField()
	recordmetadata_source = models.TextField()
	recordmetadata_recordname = models.TextField()
	recordmetadata_searchguid = models.TextField()
	recordmetadata_numberinsource = models.TextField()
	recordmetadata_zbuaminorversion = models.TextField()

	publisherdatecopyright = models.TextField()
	location = models.TextField()
	author100 = models.TextField()
	daterange = models.TextField()

	isbn = models.TextField()
	citation = models.TextField()
	keywords = models.TextField()
	abstract = models.TextField(blank = False)
	identifier = models.TextField()
	itemdatatype = models.TextField()
	itemdatahandler = models.TextField()
	created_at = models.DateTimeField()

	def get_persisted_id(self):
		return self.importedfrom.split("/")[-1]

	def ris_format(self):
		publication = self

		authors_list = publication.authors.replace("[author]", "").strip().strip(";").split(";")

		bibliographical_data = ["TY  - JOUR"]
		bibliographical_data.append("TI  - {0}".format(publication.title))
		[bibliographical_data.append("AU  - {0}".format(_a.strip())) for _a in authors_list]
		bibliographical_data.append("T2  - {0}".format(publication.containername))

		if publication.author100 and publication.author100 != "None":
			bibliographical_data.append("A2  - {0}".format(publication.author100))

		bibliographical_data.append("T3  - {0}".format(publication.publicationtype))
		bibliographical_data.append("AB  - {0}".format(publication.abstract))
		bibliographical_data.append("DA  - {0}".format(publication.year))
		bibliographical_data.append("PY  - {0}".format(publication.year))
		bibliographical_data.append("DO  - {0}".format(publication.doi))
		bibliographical_data.append("SN  - {0}".format(publication.isbn))

		# these columns needs to be filled
		bibliographical_data.append("UR  - {0}".format(""))
		bibliographical_data.append("L4  - {0}".format(""))

		additional_fields = """
			<p>Additional fields</p>
			<p>location = {0}</p>
			<p>daterange = {1}</p>
			<p>links = {2}</p>
			<p>citation = {3}</p>
			<p>identifier = {4}</p>
			<p> </p>
		""".format(
			publication.location,
			publication.daterange,
			publication.links,
			publication.citation,
			publication.identifier,
		).strip().replace("\t", "")
		bibliographical_data.append("N1  - {0}".format(additional_fields))

		recordmetadata = """
			<p>recordmetadata</p>
			<p>recordmetadata_zbuamajorversion = {0}</p>
			<p>recordmetadata_dateretrieved = {1}</p>
			<p>recordmetadata_dateconverted = {2}</p>
			<p>recordmetadata_recordtype = {3}</p>
			<p>recordmetadata_source = {4}</p>
			<p>recordmetadata_recordname = {5}</p>
			<p>recordmetadata_searchguid = {6}</p>
			<p>recordmetadata_numberinsource = {7}</p>
			<p>recordmetadata_zbuaminorversion = {8}</p>
			<p>additional metadata</p>
			<p>ephermeral_id = {9}</p>
			<p>itemdatatype = {10}</p>
			<p>itemdatahandler = {11}</p>
			<p>created_at = {12}</p>
			<p>importedfrom = {13}</p>
			<p> </p>
			<p> </p>
		""".format(
			publication.recordmetadata_zbuamajorversion,
			publication.recordmetadata_dateretrieved,
			publication.recordmetadata_dateconverted,
			publication.recordmetadata_recordtype,
			publication.recordmetadata_source,
			publication.recordmetadata_recordname,
			publication.recordmetadata_searchguid,
			publication.recordmetadata_numberinsource,
			publication.recordmetadata_zbuaminorversion,
			publication.id,
			publication.itemdatatype,
			publication.itemdatahandler,
			publication.created_at,
			publication.importedfrom,
		).strip().replace("\t", "")
		bibliographical_data.append("N1  - {0}".format(recordmetadata))

		bibliographical_data.append("ER  - ")

		return "\n".join(bibliographical_data)
