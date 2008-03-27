from zope.interface import implements
from zope.component import getSiteManager, getUtility
from zope.app.component.hooks import getSite
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from persistent import Persistent
from BTrees.OOBTree import OOBTree
from contentratings.interfaces import IUserRating
from plone.contentratings.interfaces import IRatingCategoryAssignment, IUnratable
from Products.CMFCore.interfaces import IDynamicType

class UserCategoryVocab(object):
    """Vocabulary of all categories providing IUserRating"""
    interface = IUserRating
    def __call__(self, context=None):
        """Generates a vocabulary of all the category factories available
        in a given context"""
        sm = getSiteManager(context)
        # Get all registered rating types
        categories = (c for n,c in sm.adapters.lookupAll((IDynamicType,),
                                                         self.interface))
        terms = []
        for cat in categories:
            terms.append(SimpleTerm(value=cat, token=cat.name, title=cat.title))
        return SimpleVocabulary(terms)


class LocalAssignmentUtility(Persistent):
    """A utility for determining which rating categories are available for an
    object"""
    implements(IRatingCategoryAssignment)

    def __init__(self):
        self._mapping = OOBTree()

    def _check_instance(self, content):
        return not IUnratable.providedBy(content)

    def supports_category(self, content, category):
        type_name = content.getPortalTypeName()
        # If the category is not assigned specifically to IDynamicType,
        # it should not be rejected
        if category not in self._avalable_categories:
            return True
        cat_name = category.name
        if self._check_instance and cat_name in \
               self._mapping.get(type_name, ()):
            return True

    def supported_categories(self, content):
        if not self._check_instance():
            return []
        else:
            return self.categories_for_type(content.getPortalTypeName())

    @property
    def _avalable_categories(self):
        site = getSite()
        return getUtility(IVocabularyFactory,
                                     'plone.contentratings.categories')(site)

    def assign_categories(self, portal_type, categories):
        """Check that the give names are actually valid category names,
        if so assign them to the portal_type"""
        categories = set(categories)
        available_categories = set(t.value for t in self._avalable_categories)
        assert categories.issubset(available_categories)
        self._mapping[portal_type] = set(c.name for c in categories)

    def categories_for_type(self, portal_type):
        """Returns the categories set for a given portal type"""
        names = self._mapping.get(portal_type, ())
        categories = self._avalable_categories
        return [categories.getTermByToken(n).value for n in names]
