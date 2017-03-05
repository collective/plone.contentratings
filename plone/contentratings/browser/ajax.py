from zope.component import getAdapter, getMultiAdapter
from plone.contentratings.browser.interfaces import IEditCategoryAssignment
from plone.contentratings.browser.controlpanel import AssignmentWidget
from Products.Five import BrowserView
from contentratings.interfaces import IUserRating, IEditorialRating


class ControlPanelView(BrowserView):
    """ AJAX change categories type """

    def refresh_categories(self, type_id):

        field = IEditCategoryAssignment['assignment']
        adapted = IEditCategoryAssignment(self.context)
        field = field.bind(adapted)

        widget = AssignmentWidget(field, self.request)
        widget.setPrefix('form')
        widget.setRenderedValue()
        select = widget.getSubWidget('assigned_categories')

        self.request.environ['plone.transformchain.disable'] = True
        return select.renderValue(select._getFormValue())


class RatingView(BrowserView):
    """ AJAX actions for changing and deleting ratings """
    rating_iface = IUserRating

    def update_rating(self, category, rating_class):
        """Update the user rating"""
        rating = self._extract_rating(rating_class)

        self.request.environ['plone.transformchain.disable'] = True
        return self._call_view_method(category, 'rate', value=rating)

    def delete_rating(self, category):
        """Delete the user rating"""
        self._call_view_method(category, 'remove_rating')

    def _extract_rating(self, rating_class):
        class_elements = rating_class.split(" ")
        rating = None
        for el in class_elements:
            if el.startswith('star-'):
                rating = el[5:]
        if not rating:
            raise ValueError(
                "the rating value needs to be included in method call")
        return rating

    def _get_view(self, category):
        if category == '_default':
            category = u''
        manager = getAdapter(self.context, self.rating_iface, name=category)
        view_name = manager.view_name
        return getMultiAdapter((manager, self.request), name=view_name)

    def _call_view_method(self, category, method_name, **kw):
        rating_view = self._get_view(category)
        method = getattr(rating_view, method_name)
        kw['redirect'] = False
        method(**kw)
        return rating_view()


class EditorialView(RatingView):
    """Same as above but for editorial ratings"""
    rating_iface = IEditorialRating
