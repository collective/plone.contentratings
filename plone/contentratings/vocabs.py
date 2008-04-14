from zope.interface import implements, Interface
from zope.component import getSiteManager
from zope.app.component.hooks import getSite
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IDynamicType
from contentratings.interfaces import IUserRating
from contentratings.browser.interfaces import IRatingView

class UserCategoryVocab(object):
    """Vocabulary of all categories providing IUserRating"""
    implements(IVocabularyFactory)
    interface = IUserRating
    def __call__(self, context=None):
        """Generates a vocabulary of all the category factories
        registered for IDynamicType available in a given context"""
        context = getSite()
        sm = getSiteManager(context)
        # Get all registered rating types
        categories = (c for n,c in sm.adapters.lookupAll((IDynamicType,),
                                                         self.interface))
        terms = []
        for cat in categories:
            terms.append(SimpleTerm(value=cat, token=cat.name, title=cat.title))
        return SimpleVocabulary(terms)

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

def rating_view_vocab(context):
    """All rating views fr IUserRating"""
    sm = getSiteManager(context)
    views = sm.adapters.lookupAll((IUserRating, IDefaultBrowserLayer),
                                  Interface)
    terms = []
    for name, view in views:
        if IRatingView.implementedBy(view):
            terms.append(SimpleTerm(name, name))
    return SimpleVocabulary(terms)
