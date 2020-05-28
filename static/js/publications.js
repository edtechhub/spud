$(function() {

	$("[data-toggle=tooltip]").tooltip();

	AbstractReadMore();
	if ($.cookie("abridged_abstracts") == "true")
		$("#abstract-toggle-btn").bootstrapToggle("on");
		// $("#abstract-toggle-btn").prop("checked", true);
	else
		$("#abstract-toggle-btn").bootstrapToggle("off");
		// $("#abstract-toggle-btn").prop("checked", false);
	toggleAbstractText();

	$("#abstract-toggle-btn").on("change", function() {
		var hide_abstract = $(this).prop("checked");
		$.cookie("abridged_abstracts", hide_abstract);

		toggleAbstractText();
	});

	function toggleAbstractText() {
		if ($.cookie("abridged_abstracts") == "true") {
			$(".SecSec").hide();
			$(".readMore").show();
			$(".readLess").hide();
		}
		else {
			$(".SecSec").show();
			$(".readMore").hide();
			$(".readLess").show();
		}
	}


	/*
	if ($.cookie('mark_always_flag') == "true") {
		$("#chkbx-mark_always").prop("checked", true);
		highlightFeaturedTerms();
	}

	$("#chkbx-mark_always").change(function() {
		if(this.checked) {
			$.cookie('mark_always_flag', true);
			highlightFeaturedTerms();
		}
		else {
			$.cookie('mark_always_flag', false);
		}
	});

	$("#btn-mark-now").on("click", function() {
		highlightFeaturedTerms();
	});

	function highlightFeaturedTerms() {

		var url = new URL(window.location);
		var auth = url.searchParams.get("auth");

		if (!auth || auth == undefined)
			return;

		server side tagging has been operational - so we do not need this at the moment
		$.ajax({
			url: "/keywords?auth=" + auth,

			type: 'GET',
			cache: false,

			success: function (data, status, xhr) {
				var instance = new Mark($("td.highlighter"));
				instance.mark(data.countries, {
						"className": "markCountries",
						"separateWordSearch": false,
						"accuracy": "complementary",
						"caseSensitive": true,
				});
				instance.mark(data.regions, {
						"className": "markRegions",
						"separateWordSearch": false,
						"accuracy": "complementary",
						"caseSensitive": true,
				});
				instance.mark(data.development_terms, {
						"className": "markDterms",
						"separateWordSearch": false,
						"accuracy": "complementary",
						"caseSensitive": true,
				});
			},
			error: function (jqXhr, textStatus, errorMessage) {
				alert("Issue while working with markjs");
			}
		});

		// highligh search terms
		var query = $(".form-row input[name='tak']").val();
		var search_terms = query.replace(/'/g, "").replace(/AND/g, " ").split(" ");
		search_terms = search_terms.filter(function(v){return v !== ''});

		var instance = new Mark($("td.highlighter"));
		instance.mark(search_terms, {
				"className": "markSearchTerms",
				"separateWordSearch": true,
				"caseSensitive": false,
				"accuracy": "complementary",
		});
	}
	*/

});