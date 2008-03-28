from zope.component import getAdapter, getMultiAdapter

from kss.core import kssaction, KSSExplicitError
from plone.app.kss.plonekssview import PloneKSSView

from plone.contentratings.browser.interfaces import IEditCategoryAssignment
from plone.contentratings.browser.controlpanel import AssignmentWidget
from contentratings.interfaces import IUserRating



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
        select = ksscore.getCssSelector('select[id=form.assignment.assigned_categories]')
        ksscore.replaceHTML(select, html)
        
        
class RatingKSSView(PloneKSSView):
    """ kss actions for changing and deleting ratings """
    
    @kssaction
    def update_rating(self, category, rating_class):
        """Update the user rating"""
        class_elements = rating_class.split(" ")
        rating = None
        for el in class_elements:
            if el.startswith('star-'):
                rating = el[5:]                
        if not rating:
            raise KSSExplicitError, "the rating value needs to be included in method call"
        self._call_view_method(category, 'rate', value=rating)

    @kssaction
    def delete_rating(self, category):
        """Delete the user rating"""
        self._call_view_method(category, 'remove_rating')

    def _call_view_method(self, category, method_name, **kw):
        manager = getAdapter(self.context, IUserRating, name=category)
        view_name = manager.view_name
        rating_view = getMultiAdapter((manager,self.request), name=view_name)
        method = getattr(rating_view, method_name)
        kw['redirect'] = False
        msg = method(**kw)
        html = rating_view()
        
        ksscore = self.getCommandSet('core')
        select = ksscore.getCssSelector('div.Rating#rating-stars-view-%s' % category)
        ksscore.replaceHTML(select, html)
        
        kssplone = self.getCommandSet('plone')
        kssplone.issuePortalMessage(msg)
        
        
        
        
