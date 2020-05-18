$(function() {

  $('[data-toggle=tooltip]').tooltip();

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

    if (!auth || auth == "777777")
      return;

    // highlight search terms
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

});