from zope.interface import Interface
from zope.schema import TextLine, Set, Tuple, Choice, Object, List

from contentratings.interfaces import IRatingCategory
from plone.contentratings.interfaces import _

class ICategoryAssignment(Interface):

    portal_type = Choice(title=_(u"Portal Type"),
                         required=True,
                         vocabulary="plone.contentratings.portal_types")
    assigned_categories = Set(title=_(u"Categories"),
                     value_type=Choice(title=_(u"Category"),
                                   vocabulary="plone.contentratings.categories"),
                     required=False
                     )

class IPloneRatingCategory(IRatingCategory):
    """use a vocabulary for views"""

    view_name = Choice(
        title=_(u"View"),
        description=_(u"Select the view for this category"),
        vocabulary='plone.contentratings.rating_views',
        required=True,
        )

class IEditCategoryAssignment(Interface):

    assignment = Object(ICategoryAssignment,
                   title=_(u"Assignment"),
                   required=False)


class ICategoryContainer(Interface):

    local_categories = List(title=_(u"Local Categories"),
                            value_type=Object(IPloneRatingCategory,
                                              title=_(u"Category")),
                            required=False)

    acquired_categories = Tuple(title=_(u"Acquired Categories"),
                                value_type=Object(IPloneRatingCategory,
                                                  title=_(u"Category")),
                                readonly=True,
                                required=False,
                                )
