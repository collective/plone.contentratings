from zope.interface import implements
from zope.component import adapts

from Products.CMFCore.utils import getToolByName

from plone.app.controlpanel.form import ControlPanelForm
from plone.fieldsets.fieldsets import FormFieldsets
from zope.app.form.browser.objectwidget import ObjectWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile 

from zope.app.component.interfaces import ISite
from zope.formlib import form

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.i18n import translate

from plone.contentratings.interfaces import _

from plone.contentratings.interfaces import IRatingCategoryAssignment
from plone.contentratings.browser.interfaces import IEditCategoryAssignment
from plone.contentratings.browser.interfaces import ICategoryAssignment
from plone.contentratings.browser.interfaces import ICategoryContainer
from plone.contentratings.browser.category_manage import hr_categories_widget, display_categories_widget
from plone.contentratings.interfaces import IRatingCategoryAssignment


class CategoryAssignment(object):
    """A Dummy type which is simply used to hold attributes, those
    attbributes are set by the form"""
    implements(ICategoryAssignment)


class AssignmentsAdapter(object):
    """An adapter from the site to IEditCategoryAssignment which uses
    the local IRatingCategoryAssignment utility, to set rating
    category to portal type assignments.

    We need a utility and a portal::

        >>> class DummyUtil(object):
        ...     mapping = {}
        ...     def assign_categories(self, ptype, categories):
        ...         self.mapping[ptype] = categories
        >>> class DummyPortal(object):
        ...     portal_types = None
        ...     plone_utils = None
        >>> from zope.app.testing import ztapi
        >>> from plone.contentratings.interfaces import IRatingCategoryAssignment
        >>> util = DummyUtil()
        >>> ztapi.provideUtility(IRatingCategoryAssignment, util)
        >>> portal = DummyPortal()

    Now let's use our adapter::

        >>> from plone.contentratings.browser.controlpanel import AssignmentsAdapter
        >>> from plone.contentratings.browser.controlpanel import CategoryAssignment
        >>> assigner = AssignmentsAdapter(portal)
        >>> assignment1 = CategoryAssignment()
        >>> assignment1.portal_type = 'test'
        >>> assignment1.assigned_categories = ['cat1', 'cat2']
        >>> assigner.assignment = assignment1
        >>> util.mapping
        {'test': ['cat1', 'cat2']}
        >>> assignment1.assigned_categories = []
        >>> assigner.assignment = assignment1
        >>> util.mapping
        {'test': []}
        >>> assignment1.portal_type = 'another'
        >>> assigner.assignment = assignment1
        >>> util.mapping
        {'test': [], 'another': []}

    """
    implements(IEditCategoryAssignment)
    adapts(ISite)

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
    """A custom version of ObjectWidget which sets CategoryAssignment
    objects on the context (which is the above adapter).  The value
    in the widget is the list of selected categories for the type
    specified in the request.

    We need a request and a field for our widget to act on::

        >>> from zope.publisher.browser import TestRequest
        >>> request = TestRequest()
        >>> class Dummy(object):
        ...     pass
        >>> content = Dummy()
        >>> content.assignment = None
        >>> content.context = None
        >>> from plone.contentratings.browser.interfaces import IEditCategoryAssignment
        >>> field = IEditCategoryAssignment['assignment'].bind(content)
        >>> from plone.contentratings.browser.controlpanel import AssignmentWidget

    We also need vocabularies of portal types and categories, and a type
    assignment utility::

        >>> from zope.schema.vocabulary import SimpleVocabulary, getVocabularyRegistry
        >>> def type_vocab(context):
        ...     return SimpleVocabulary.fromItems((('type1', 'type1'),
        ...                                        ('type2', 'type2')))
        >>> def category_vocab(context):
        ...     return SimpleVocabulary.fromItems((('cat1', 'cat1'),
        ...                                        ('cat2', 'cat2')))
        >>> registry = getVocabularyRegistry()
        >>> registry.register('plone.contentratings.portal_types', type_vocab)
        >>> registry.register('plone.contentratings.categories', category_vocab)
        >>> from zope.app.testing import ztapi
        >>> ztapi.provideUtility(IVocabularyFactory, type_vocab,
        ...                      name='plone.contentratings.portal_types')
        >>> ztapi.provideUtility(IVocabularyFactory, category_vocab,
        ...                      name='plone.contentratings.categories')
        >>> class DummyUtil(object):
        ...     def categories_for_type(self, portal_type):
        ...         return ['cat2', 'fake_cat+%s'%portal_type]
        >>> from plone.contentratings.interfaces import IRatingCategoryAssignment
        >>> ztapi.provideUtility(IRatingCategoryAssignment, DummyUtil())

   Now that we have our vocabularies and sub-widgets, we can test our widget's
   custom behavior.  First we see that when we set the rendered value
   the first portal type is retrieved, along with the category
   settings for that type::

        >>> widget = AssignmentWidget(field, request)
        >>> type_widget = widget.getSubWidget('portal_type')
        >>> category_widget = widget.getSubWidget('assigned_categories')
        >>> type_widget._data is type_widget._data_marker
        True
        >>> category_widget._data is category_widget._data_marker
        True
        >>> widget.setRenderedValue('nonsense')
        >>> type_widget._data
        'type1'
        >>> category_widget._data
        set(['fake_cat+type1', 'cat2'])

    If a portal_type is specfied in the form (using either of two
    request variables), then the categories retrieved are those for
    that type::

        >>> request.form['form.assignment.portal_type'] = 'type2'
        >>> widget.setRenderedValue('nonsense')
        >>> type_widget._data
        'type2'
        >>> category_widget._data
        set(['cat2', 'fake_cat+type2'])

        >>> request.form['type_id'] = 'type3'
        >>> widget.setRenderedValue('nonsense')
        >>> type_widget._data
        'type3'
        >>> category_widget._data
        set(['cat2', 'fake_cat+type3'])

    If were to submit the form, an assignment object would be created and
    set on our content/adapter::

        >>> request.form['field.assignment.portal_type'] = 'type1'
        >>> request.form['field.assignment.assigned_categories'] = ['cat1']
        >>> widget.applyChanges(content)
        True
        >>> isinstance(content.assignment, CategoryAssignment)
        True
        >>> content.assignment.portal_type
        'type1'
        >>> content.assignment.assigned_categories
        set(['cat1'])

    """

    def __init__(self, context, request, **kw):
        super(AssignmentWidget, self).__init__(context, request,
                                               CategoryAssignment)

    def setRenderedValue(self, value=None):
        """Uses the currently selected categories as the current value,
        regardless of the passed in value."""
        value = self.get_categories()
        super(AssignmentWidget, self).setRenderedValue(value)


    def get_categories(self):
        """Return the list of categories assigned to the type specified in
        the request."""
        # Look for the portal_type in the request
        portal_type = self.request.form.get('type_id',
                           self.request.form.get('form.assignment.portal_type',
                                                 None))
        if portal_type is None:
            # get the vocabulary of types and choose the first entry, since
            # that's the one selected if one was not explicitly selected.
            vocab_factory = getUtility(IVocabularyFactory,
                          name="plone.contentratings.portal_types")
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
categories.description = _(u'Add, modify, or remove rating categories.  You '
u'may specify a title, description, conditions for viewing and setting '
u'ratings, a view to display the rating, and a relative order number.  '
u'Categories which are defined at a lower level (e.g., globally) may not be '
u'edited. You need to save your changes after adding or removing categories')

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
        """Does nothing except reload the form"""
        type_id = self.request.form['form.assignment.portal_type']
        self.request.form.clear()
        self.request.form['type_id'] = type_id
        return self()

