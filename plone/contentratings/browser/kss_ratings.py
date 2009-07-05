from zope.component import getAdapter, getMultiAdapter, getUtility
from zope.schema.interfaces import IVocabularyFactory

from kss.core import kssaction, KSSExplicitError
from plone.app.kss.plonekssview import PloneKSSView

from plone.contentratings.interfaces import IRatingCategoryAssignment
from plone.contentratings.browser.interfaces import IEditCategoryAssignment
from plone.contentratings.browser.controlpanel import AssignmentWidget
from plone.contentratings.browser.controlpanel import selected_categories
from contentratings.interfaces import IUserRating, IEditorialRating


class ControlPanelKSSView(PloneKSSView):
    """ kss change categories type """

    @kssaction
    def refresh_categories(self, type_id):
        
        field = IEditCategoryAssignment['assignment']
        adapted = IEditCategoryAssignment(self.context)
        field = field.bind(adapted)
        
        widget = AssignmentWidget(field, self.request)
        widget.setPrefix('form')
        widget.setRenderedValue()
        select = widget.getSubWidget('assigned_categories')
        html = select.renderValue(select._getFormValue())
        
        ksscore = self.getCommandSet('core')
        select = ksscore.getCssSelector(
            'select[id="form.assignment.assigned_categories"]')
        ksscore.clearChildNodes(select)
        ksscore.replaceHTML(select, html)
        
    @kssaction
    def save_rating_assignments(self):
        """Save the rating assignments in the current form"""
        req =self.request
        p_type = req.get('form.assignment.portal_type', '')
        assignments = set(req.get('form.assignment.assigned_categories', ()))
        util = getUtility(IRatingCategoryAssignment)
        current_selection = selected_categories(p_type)
        if set(c.name for c in current_selection) != assignments:
            categories = list(getUtility(IVocabularyFactory,
                         name='plone.contentratings.categories')(self.context))
            util.assign_categories(p_type,
                                   [c.value for c in categories
                                                     if c.token in assignments])


class RatingKSSView(PloneKSSView):
    """ kss actions for changing and deleting ratings """
    rating_iface = IUserRating
    base_selector = '.Rating#rating-stars-view-'

    @kssaction
    def update_rating(self, category, rating_class):
        """Update the user rating"""
        rating = self._extract_rating(rating_class)
        self._call_view_method(category, 'rate', value=rating)

    @kssaction
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
            raise KSSExplicitError, "the rating value needs to be included in "\
                                    "method call"
        return rating

    def _get_view(self, category):
        if category == '_default':
            category = u''
        manager = getAdapter(self.context, self.rating_iface, name=category)
        view_name = manager.view_name
        return getMultiAdapter((manager,self.request), name=view_name)

    def _call_view_method(self, category, method_name, **kw):
        rating_view = self._get_view(category)
        method = getattr(rating_view, method_name)
        kw['redirect'] = False
        msg = method(**kw)
        self._update_page(rating_view, msg)

    def _update_page(self, rating_view, msg=''):
        html = rating_view()
        category = rating_view.context.name
        ksscore = self.getCommandSet('core')
        select = ksscore.getCssSelector(self.base_selector +
                                         (category or '_default'))
        ksscore.replaceHTML(select, html)

        if msg:
            kssplone = self.getCommandSet('plone')
            kssplone.issuePortalMessage(msg)


class EditorialKSSView(RatingKSSView):
    """Same as above but for editorial ratings"""
    rating_iface = IEditorialRating
    base_selector = '.EditorRating#editor-rating-stars-view-'
