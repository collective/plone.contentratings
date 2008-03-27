from zope.interface import Interface
from zope.schema import TextLine, Set, Tuple, Choice, Object, List

from contentratings.interfaces import IRatingCategory, _

class ICategoryAssignment(Interface):

    portal_type = Choice(title=_(u"Portal Type"),
                         required=True,
                         vocabulary="plone.contentratings.portal_types")
    assigned_categories = Set(title=_(u"Categories"),
                     value_type=Choice(title=_(u"Category"),
                                   vocabulary="plone.contentratings.categories")
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
                   title=_(u"Assignment"))


class ICategoryContainer(Interface):
    
    categories = List(title=_(u"Categories"),
                      value_type=Object(IPloneRatingCategory,
                                        title=u"Category"))
                                        

class ITTWCategory(Interface):
    """marker interface for categories created through the web.
       (let us recognize them when in the configlet)"""
    