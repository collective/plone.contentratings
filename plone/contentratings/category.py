from AccessControl import getSecurityManager
from contentratings.category import RatingCategoryAdapter
from zope.component import queryUtility, adapts
from plone.contentratings.interfaces import IRatingCategoryAssignment
from contentratings.interfaces import IRatingCategory
from zope.tales.engine import Engine
from Products.CMFCore.interfaces import IDynamicType
from Products.CMFCore.utils import getToolByName

class PloneRatingCategoryAdapter(RatingCategoryAdapter):
    """A rating category adapter for IDynamicType, which looks up
    and potentially rejects rating assignments based on a utility
    lookup.  It also uses Zope 2 machinery to looup up the current user."""
    adapts(IRatingCategory, IDynamicType)


    def __new__(cls, category, context):
        """Use the Assignment utility to verify that a type supports
        the given category."""
        util = queryUtility(IRatingCategoryAssignment)
        # The category only applies to the content if an assignment util
        # exists and approves the category
        if util is None or not util.supports_category(context, category):
            return None
        # sub classes shouldn't implement __new__
        return super(PloneRatingCategoryAdapter, cls).__new__(cls)

    def _get_user(self):
        """Use Zope 2 security to lookup the current user"""
        return getSecurityManager().getUser()

    def _getExprContext(self):
        """A plone specific expression context"""
        context = self.context
        portal = getToolByName(context, 'portal_url').getPortalObject()
        pm = getToolByName(context, 'portal_membership')
        return Engine.getContext({'context': context,
                                  'user': self._get_user(),
                                  'portal': portal,
                                  'checkPermission': pm.checkPermission})
