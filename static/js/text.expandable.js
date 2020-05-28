function AbstractReadMore() {
	//This limit you can set after how much characters you want to show Read More.
	var carLmt = 100;
	// Text to show when text is collapsed
	var readMoreTxt = " ... Read More";
	// Text to show when text is expanded
	var readLessTxt = " Read Less";

	//Traverse all selectors with this class and manupulate HTML part to show Read More
	$(".addReadMore").each(function() {
		if ($(this).find(".firstSec").length)
			return;

		var allstr = $(this).html();
		var updatedCarLmt = carLmt + 5;

		if (allstr.length > carLmt) {
			var firstSet = allstr.substring(0, updatedCarLmt);

			var spanOpenCount = (firstSet.match(/<span/g) || []).length;
			var spanCloseCount = (firstSet.match(/<\/span>/g) || []).length;
			if (spanOpenCount > spanCloseCount) {
				while (spanOpenCount != spanCloseCount) {
					for (var index = 0; index < spanOpenCount - spanCloseCount; index++) {
						updatedCarLmt = allstr.indexOf("</span>", updatedCarLmt) + 7;

						firstSet = allstr.substring(0, updatedCarLmt);
					}

					spanOpenCount = (firstSet.match(/<span/g) || []).length;
					spanCloseCount = (firstSet.match(/<\/span>/g) || []).length;
				}
			}
			else {
				updatedCarLmt = carLmt;
				firstSet = allstr.substring(0, updatedCarLmt);
			}

			var secdHalf = allstr.substring(updatedCarLmt, allstr.length);
			var strtoadd = firstSet + "<span class='SecSec'>" + secdHalf + "</span><span class='readMore'  title='Click to Show More'>" + readMoreTxt + "</span><span class='readLess' title='Click to Show Less'>" + readLessTxt + "</span>";
			$(this).html(strtoadd);
		}

	});

	$(document).on("click", ".readMore,.readLess", function() {
		$(this).closest(".addReadMore").toggleClass("showlesscontent showmorecontent");
	});
}
