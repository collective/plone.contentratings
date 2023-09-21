from Products.CMFCore.utils import getToolByName
from zope.component import adapts
from zope.component import getUtility
from zope.component.interfaces import ISite
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from z3c.form import form
from z3c.form.object import FactoryAdapter

from contentratings.category import RatingsCategoryFactory
from plone.autoform.form import AutoExtensibleForm
from plone.contentratings.interfaces import _
from plone.contentratings.interfaces import IRatingCategoryAssignment
from plone.contentratings.browser.interfaces import ICategoryAssignment
from plone.contentratings.browser.interfaces import IEditCategoryAssignment
from plone.contentratings.browser.interfaces import IControlPanelForm


@implementer(ICategoryAssignment)
class CategoryAssignment(object):
    """A Dummy type which is simply used to hold attributes, those
    attbributes are set by the form"""


@implementer(IEditCategoryAssignment)
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
        factory = CategoryAssignmentFactory(self.context,
                                            getattr(self.context, 'REQUEST', None),
                                            None, None)
        return factory()

    assignment = property(fget=_get_assignment, fset=_set_assignment)


def selected_categories(portal_type):
    assignments = getUtility(IRatingCategoryAssignment)
    return (t for t in assignments.categories_for_type(portal_type))


class CategoryAssignmentFactory(FactoryAdapter):

    def __call__(self, value=None):
        if not self.request:
            portal_type = None
        else:
            portal_type = self.request.form.get(
                'type_id',
                self.request.form.get('form.widgets.assignment.widgets.portal_type',
                                      None)
            )
        if portal_type is None:
            # get the vocabulary of types and choose the first entry, since
            # that's the one selected if one was not explicitly selected.
            vocab_factory = getUtility(
                IVocabularyFactory,
                name="plone.contentratings.portal_types"
            )
            portal_type = list(vocab_factory(self.context))[0].token

        assignment = CategoryAssignment()
        assignment.portal_type = portal_type
        assignment.assigned_categories = set(selected_categories(portal_type))
        assignment.context = self.context

        return assignment


class RatingCategoryFactory(FactoryAdapter):

    def __call__(self, value=None):
        if not value:
            value = {}
        return RatingsCategoryFactory(**value)


class ContentRatingsControlPanel(AutoExtensibleForm, form.EditForm):

    form_name = _(u"Category Assignments")
    label = _(u"Rating settings")
    id = "contentratings-controlpanel"
    control_panel_view = "contentratings-controlpanel"
    description = _(u"Settings related to content ratings.")
    schema = IControlPanelForm
