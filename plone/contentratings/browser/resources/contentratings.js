jQuery(function($) {

var baseUrl = $('base').attr('href') || $('body').attr('data-base-url') || window.PORTAL_URL || '';
var kssAttr = function (el, name) {
	var $el = $(el).closest('[class*="kssattr-' + name + '-"]');
	var klass = $el.attr('class');
	return klass.match('kssattr-' + name + '-(\\S+)')[1];
}

var $change_type = $('input[name="form.actions.change_type"]')
$change_type.hide();

var $portal_type = $('select[name^="form.widgets.assignment.widgets.portal_type"]');
$portal_type.change(function () {
	$.getJSON(baseUrl + '/refreshCategories', {type_id: $(this).val()}, function (data) {
		var $select = $('select[name^="form.widgets.assignment.widgets.assigned_categories"]');
		data = data || [];
		$('option', $select).each(function (i, e) {
			if (data.indexOf(e.value) >= 0) {
				$(e).prop('selected', true);
			} else {
				$(e).prop('selected', false);
			}
		});
	});
});

var token = $('#protect-script').attr('data-token');

$(document).on('click', '.Rating ul.star-rating a.rate', function (e) {
	e.preventDefault();
	var category = kssAttr(this, 'category') || 'default';
	$.post(baseUrl + '/updateRating', {
		rating_class: $(this).attr('class'),
		category: category,
		_authenticator: token
	}, function (data) {
		$('.Rating#rating-stars-view-' + category).replaceWith(data);
	});
});

$(document).on('click', '.Rating .UserRating a.DeleteRating', function (e) {
	e.preventDefault();
	var category = kssAttr(this, 'category') || 'default';
	$.post(baseUrl + '/deleteRating', {
		category: category,
		_authenticator: token
	}, function (data) {
		$('.Rating#rating-stars-view-' + category).replaceWith(data);
	});
});

$(document).on('click', '.EditorRating ul.star-rating a.rate', function (e) {
	e.preventDefault();
	var category = kssAttr(this, 'category') || 'default';
	$.post(baseUrl + '/updateEditorRating', {
		rating_class: $(this).attr('class'),
		category: category,
		_authenticator: token
	}, function (data) {
		$('.EditorRating#editor-rating-stars-view-' + category).replaceWith(data);
	});
});

});
