from zope.interface import implements
from zope.component import adapts

from plone.contentratings.interfaces import IRatingCategoryAssignment
from Products.CMFCore.utils import getToolByName

from plone.app.controlpanel.form import ControlPanelForm
from plone.fieldsets.fieldsets import FormFieldsets
from zope.app.form.browser.objectwidget import ObjectWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile 

from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.formlib import form

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.i18n import translate

from contentratings.interfaces import _

from plone.contentratings.browser.interfaces import IEditCategoryAssignment
from plone.contentratings.browser.interfaces import ICategoryAssignment
from plone.contentratings.browser.interfaces import ICategoryContainer
from plone.contentratings.browser.category_manage import categories_widget
from plone.contentratings.interfaces import IRatingCategoryAssignment


from plone.app.kss.plonekssview import PloneKSSView
from kss.core import kssaction
from plone.app.kss.interfaces import IPloneKSSView


class CategoryAssignment(object):
    implements(ICategoryAssignment)


class AssignmentsAdapter(object):
    implements(IEditCategoryAssignment)
    adapts(IPloneSiteRoot)

    def __init__(self, context):
        self.context = context
        self.util = getUtility(IRatingCategoryAssignment)
        # need these for vocabulary lookup
        self.portal_types = getToolByName(context, 'portal_types')
        self.plone_utils = getToolByName(context, 'plone_utils')

    def _set_assignment(self, assignment):
        self.util.assign_categories(assignment.portal_type, 
                                    assignment.assigned_categories)

    def _get_assignment(self):
        return None

    assignment = property(fget=_get_assignment, fset=_set_assignment)

        

class AssignmentWidget(ObjectWidget):
    
    def __init__(self, context, request, **kw):
        super(AssignmentWidget, self).__init__(context, request, CategoryAssignment)
        
    def setRenderedValue(self, value=None):
        value = self.get_categories()
        super(AssignmentWidget, self).setRenderedValue(value)

 
    def get_categories(self):
        portal_type = self.request.form.get('type_id', 
                                            self.request.form.get('form.assignment.portal_type', None))
        if portal_type is None:
            vocab_factory = getUtility(IVocabularyFactory,
                                        name="plone.app.vocabularies.ReallyUserFriendlyTypes")
            portal_type = list(vocab_factory(self.context.context.context))[0].token
        
        assignment = CategoryAssignment()
        assignment.portal_type = portal_type
        assignment.assigned_categories = set(selected_categories(portal_type))
        
        return assignment
    
    
def selected_categories(portal_type):
    assignments = getUtility(IRatingCategoryAssignment)
    return (t for t in assignments.categories_for_type(portal_type))

    

typespolicies = FormFieldsets(IEditCategoryAssignment)
typespolicies.id = 'types_categories'
typespolicies.label = _(u'Portal Types Categories')

categories = FormFieldsets(ICategoryContainer)
categories.id = 'manage_categories'
categories.label = _(u'Manage Categories')

class ContentRatingsControlPanel(ControlPanelForm):
    
    form_name = _(u"Category Assignments")
    
    actions = ControlPanelForm.actions.copy()

    label = _(u"Set the categories for portal types")
    description = _(u"Settings related to content ratings.")
    
    typespolicies['assignment'].custom_widget = AssignmentWidget
    
    categories['categories'].custom_widget = categories_widget
    form_fields = FormFieldsets(typespolicies, categories)
        
    @form.action(_(u'Change Portal Type'), name=u'change_type')
    def change_type(self, action, data):
        type_id = self.request.form['form.assignment.portal_type']
        self.request.form.clear()
        self.request.form['type_id'] = type_id
        return self()




class ControlPanelKSSView(PloneKSSView):
    """ kss change categories type """

    implements(IPloneKSSView)

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
        
