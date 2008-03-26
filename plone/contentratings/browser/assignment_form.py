from zope.interface import implements
from zope.component import adapts, getUtility
from zope.app.component.hooks import getSite
from zope.formlib import form
from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import SequenceWidget, ObjectWidget
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from Products.Five.formlib import formbase
from plone.contentratings.browser.interfaces import ICategoryAssignment
from plone.contentratings.browser.interfaces import IEditCategoryAssignments
from plone.contentratings.interfaces import IRatingCategoryAssignment
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName


def types_vocab(context):
    """Types Vocabulary which doesn't freak out during validation"""
    context = getattr(context, 'context', context) or getSite()
    ptool = getToolByName(context, 'plone_utils', None)
    ttool = getToolByName(context, 'portal_types', None)
    if ptool is None or ttool is None:
        return None
    items = [ (ttool[t].Title(), t)
              for t in ptool.getUserFriendlyTypes() ]
    items.sort()
    items = [SimpleTerm(i[1], i[1], i[0]) for i in items]
    return SimpleVocabulary(items)

class CategoryAssignment(object):
    implements(ICategoryAssignment)
    portal_type = None
    categories = set()

class AssignmentsAdapter(object):
    implements(IEditCategoryAssignments)
    adapts(ISiteRoot)

    def __init__(self, context):
        self.context = context
        self.util = getUtility(IRatingCategoryAssignment)
        # need these for vocabulary lookup
        self.portal_types = getToolByName(context, 'portal_types')
        self.plone_utils = getToolByName(context, 'plone_utils')

    def _set_list(self, list):
        self.util._mapping.clear()
        assign = self.util.assign_categories
        for assignment in list:
            assign(assignment.portal_type, assignment.categories)

    def _get_list(self):
        items = []
        util = self.util
        for ptype in util._mapping.keys():
            assignment = CategoryAssignment()
            assignment.portal_type = ptype
            assignment.categories = set(util.categories_for_type(ptype))
            items.append(assignment)
        return tuple(items)

    types = property(fget=_get_list, fset=_set_list)

assignment_widget = CustomWidgetFactory(ObjectWidget, CategoryAssignment)
assignments_widget = CustomWidgetFactory(SequenceWidget, assignment_widget)

class AssignmentForm(formbase.EditForm):
    """A form for editing the assignment utility"""

    form_fields = form.FormFields(IEditCategoryAssignments)

    label = u"Set the categories for portal types"

    form_fields['types'].custom_widget = assignments_widget
