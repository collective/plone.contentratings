from zope.interface import Interface
from zope.schema import TextLine, Set, Tuple, Choice, Object

class ICategoryAssignment(Interface):

    portal_type = Choice(title=u"Portal Type",
                         required=True,
                         vocabulary="plone.contentratings.portal_types")
    categories = Set(title=u"Categories",
                     value_type=Choice(title=u"Category",
                                   vocabulary="plone.contentratings.categories")
                     )

class IEditCategoryAssignments(Interface):

    types = Tuple(title=u"Portal Type Assignments",
                  value_type=Object(ICategoryAssignment,
                                    title=u"Assignment"))
