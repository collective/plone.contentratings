from contentratings.interfaces import IRatingCategory
from zope.interface import Interface
from zope.schema import Set, Tuple, Choice, Object, List

from plone.contentratings.interfaces import _
try:
    from plone.supermodel.model import Schema, fieldset
except ImportError:
    from plone.directives.form import Schema, fieldset


class ICategoryAssignment(Interface):

    portal_type = Choice(
        title=_(u"Portal Type"),
        required=True,
        vocabulary="plone.contentratings.portal_types")
    assigned_categories = Set(
        title=_(u"Categories"),
        value_type=Choice(title=_(u"Category"),
                          vocabulary="plone.contentratings.categories"),
        required=False)


class IPloneRatingCategory(IRatingCategory):
    """use a vocabulary for views"""

    view_name = Choice(
        title=_(u"View"),
        description=_(u"Select the view for this category"),
        vocabulary='plone.contentratings.rating_views',
        required=True)


class IEditCategoryAssignment(Interface):

    assignment = Object(
        ICategoryAssignment,
        title=_(u"Assignment"),
        required=False)


class ICategoryContainer(Interface):

    local_categories = List(
        title=_(u"Local Categories"),
        value_type=Object(IPloneRatingCategory,
                          title=_(u"Category")),
        required=False)

    acquired_categories = Tuple(
        title=_(u"Acquired Categories"),
        value_type=Object(IPloneRatingCategory,
                          title=_(u"Category")),
        readonly=True,
        required=False)


class IControlPanelForm(Schema, ICategoryContainer, IEditCategoryAssignment):
    fieldset(
        'types_categories',
        label=_(u"Rating Assignments"),
        description=_(
            'typespolicies_description_help',
            default=u"""Choose a portal type from the list and select
one or more rating categories to appear on that type."""
        ),
        fields=['assignment']
    )

    fieldset(
        'manage_categories',
        label=_(u"Manage Categories"),
        description=_(
            'categories_description_help',
            default=u"""Add, modify, or remove rating categories. You
may specify a title, description, conditions for viewing and setting
ratings, a view to display the rating, and a relative order number.
Categories which are defined at a lower level (e.g., globally) may not be
edited. You need to save your changes after adding or removing categories"""
        ),
        fields=['local_categories', 'acquired_categories']
    )
