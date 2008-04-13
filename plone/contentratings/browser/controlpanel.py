from zope.interface import implements
from zope.component import adapts

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

from plone.contentratings.interfaces import IRatingCategoryAssignment
from plone.contentratings.browser.interfaces import IEditCategoryAssignment
from plone.contentratings.browser.interfaces import ICategoryAssignment
from plone.contentratings.browser.interfaces import ICategoryContainer
from plone.contentratings.browser.category_manage import hr_categories_widget, display_categories_widget
from plone.contentratings.interfaces import IRatingCategoryAssignment


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
typespolicies.label = _(u'Rating Assignments')
typespolicies.description = _(u'Choose a portal type from the list and select '
u'one or more rating categories to appear on that type. ')
typespolicies.required = False

categories = FormFieldsets(ICategoryContainer)
categories.id = 'manage_categories'
categories.label = _(u'Manage Categories')
categories.description = _(u'Add, modify, or remove rating categories.  You may '
u'specify a title, description, conditions for viewing and setting ratings, '
u'a view to display the rating, and a relative order number.  Categories which are '
u'defined at a lower level (e.g., globally) may not be edited. '
u'You need to save your changes after adding or removing categories')
categories.required = False

class ContentRatingsControlPanel(ControlPanelForm):
    
    form_name = _(u"Category Assignments")
    
    actions = ControlPanelForm.actions.copy()

    label = _(u"Set the categories for portal types")
    description = _(u"Settings related to content ratings.")
    
    typespolicies['assignment'].custom_widget = AssignmentWidget
    
    categories['local_categories'].custom_widget = hr_categories_widget
    categories['acquired_categories'].custom_widget = display_categories_widget
    form_fields = FormFieldsets(typespolicies, categories)
        
    @form.action(_(u'Change Portal Type'), name=u'change_type')
    def change_type(self, action, data):
        type_id = self.request.form['form.assignment.portal_type']
        self.request.form.clear()
        self.request.form['type_id'] = type_id
        return self()

