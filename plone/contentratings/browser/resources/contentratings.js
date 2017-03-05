jQuery(function($) {

var baseUrl = $('base').attr('href');
var kssAttr = function (el, name) {
	var $el = $(el).closest('[class*="kssattr-' + name + '-"]');
	var klass = $el.attr('class');
	return klass.match('kssattr-' + name + '-(\\S+)')[1];
}

var $change_type = $('input[name="form.actions.change_type"]')
$change_type.hide();

var $portal_type = $('select[name="form.assignment.portal_type"]');
$portal_type.change(function () {
	$.get(baseUrl + '/refreshCategories', {type_id: $(this).val()}, function (data) {
		$('select[id="form.assignment.assigned_categories"]').replaceWith(data);
	});
});

$(document).on('click', '.Rating ul.star-rating a.rate', function (e) {
	e.preventDefault();
	var category = kssAttr(this, 'category') || 'default';
	$.post(baseUrl + '/updateRating', {
		rating_class: $(this).attr('class'),
		category: category
	}, function (data) {
		$('.Rating#rating-stars-view-' + category).replaceWith(data);
	});
});

$(document).on('click', '.Rating .UserRating a.DeleteRating', function (e) {
	e.preventDefault();
	var category = kssAttr(this, 'category') || 'default';
	$.post(baseUrl + '/deleteRating', {
		category: category
	}, function (data) {
		$('.Rating#rating-stars-view-' + category).replaceWith(data);
	});
});

$(document).on('click', '.EditorRating ul.star-rating a.rate', function (e) {
	e.preventDefault();
	var category = kssAttr(this, 'category') || 'default';
	$.post(baseUrl + '/updateEditorRating', {
		rating_class: $(this).attr('class'),
		category: category
	}, function (data) {
		$('.EditorRating#editor-rating-stars-view-' + category).replaceWith(data);
	});
});

});
