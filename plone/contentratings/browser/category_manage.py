from zope.interface import implements, alsoProvides
from zope.component import adapts, getSiteManager, queryUtility
from zope.app.component import queryNextSiteManager
from zope.app.form import CustomWidgetFactory
from zope.app.form.interfaces import MissingInputError
from zope.app.form.browser import ObjectWidget, ListSequenceWidget, SequenceDisplayWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.schema import getFieldsInOrder
from zope.app.component.interfaces import ISite

from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.contentratings.browser.interfaces import ICategoryContainer
from contentratings.interfaces import IUserRating
from contentratings.interfaces import IRatingCategory, _
from contentratings.category import RatingsCategoryFactory

from Products.CMFCore.interfaces import IDynamicType

class CategoryContainerAdapter(object):
    """Adapter for site root to ICategoryContainer.  This provides mechanisms
    for introspecting the registered categories (adapters) at a particular
    site, as well as adding, removing and modifying categories.

    We have a local site setup, we can adapt that to demonstrate
    the expected behavior::

        >>> from plone.contentratings.browser.category_manage import CategoryContainerAdapter
        >>> manager = CategoryContainerAdapter(site)
        >>> manager.local_categories
        []
        >>> manager.acquired_categories
        []

    The acquired categories come from the global site manager (or any other
    site managers in the site).  So if we add a global category it
    ends up there::

        >>> from contentratings.category import RatingsCategoryFactory
        >>> category1 = RatingsCategoryFactory('cat1', name='cat1')
        >>> from contentratings.interfaces import IUserRating
        >>> from Products.CMFCore.interfaces import IDynamicType
        >>> from zope.app.testing import ztapi
        >>> ztapi.provideAdapter((IDynamicType,), IUserRating,
        ...                      category1, name='cat1')
        >>> manager.local_categories
        []
        >>> manager.acquired_categories # doctest: +ELLIPSIS
        [<contentratings.category.RatingsCategoryFactory object at ...>]

    We can use the adapter to add local categories, which are registered
    with the local site manager::

        >>> category2 = RatingsCategoryFactory('cat2', name='cat2')
        >>> manager.add(category2)
        >>> len(manager.local_categories)
        1
        >>> manager.local_categories[0].name
        'cat2'
        >>> from zope.component import getSiteManager, getGlobalSiteManager
        >>> sm = getSiteManager()
        >>> adapter = sm.adapters.lookup((IDynamicType,), IUserRating, name='cat2')
        >>> adapter.name
        'cat2'

    We can verify that the adapter was registered locally, not globally:

        >>> gsm = getGlobalSiteManager()
        >>> gsm.adapters.lookup((IDynamicType,), IUserRating, name='cat2') is None
        True

    We can also remove a category from the local site manager::

        >>> manager.remove(category2)
        >>> manager.local_categories
        []
        >>> sm.adapters.lookup((IDynamicType,), IUserRating, name='cat2') is None
        True

    We cannot remove a category from another site manager though::

        >>> manager.remove(category1) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        AssertionError

    The manager also allows in place modifications of rating
    categories.  To modify a category, you can call the modify method
    with a category of the same name and different attributes, the
    changed attributes will be altered on the existing category::

        >>> manager.add(category2)
        >>> category2_new = RatingsCategoryFactory('New Category 2', name='cat2')
        >>> manager.modify(category2_new)
        >>> category2.title
        'New Category 2'
        >>> sm.adapters.lookup((IDynamicType,), IUserRating,
        ...                    name='cat2') is category2
        True

    Trying to modify a category from the global site manager will fail though::

        >>> category1_new = RatingsCategoryFactory('New Category 1', name='cat1')
        >>> manager.modify(category1_new) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        AssertionError


    The manager's 'local_categories' attribute can be set directly, which
    triggers, modifications, adds and deletes as necessary::

        >>> category2_new.title = 'Another Change'
        >>> category2_new.order = 200
        >>> category3 = RatingsCategoryFactory('cat3', name='cat3')
        >>> manager.local_categories = [category2_new, category3]
        >>> len(manager.local_categories)
        2
        >>> manager.local_categories[0].name
        'cat3'
        >>> manager.local_categories[1].name
        'cat2'

    Note that the 'cat2' has beenmodified in place::

        >>> manager.local_categories[1].title
        'Another Change'
        >>> manager.local_categories[1].order
        200
        >>> manager.local_categories[1] is category2
        True

    A global category can be overridden by adding one with the same name
    locally, though the global registration remains::

        >>> category1_new.order = 200
        >>> manager.local_categories = [category3, category1_new]
        >>> len(manager.local_categories)
        2
        >>> manager.local_categories[0].name
        'cat3'
        >>> manager.local_categories[1].name
        'cat1'
        >>> manager.local_categories[1] is category1_new
        True
        >>> sm.adapters.lookup((IDynamicType,), IUserRating, name='cat3') is category3
        True
        >>> sm.adapters.lookup((IDynamicType,), IUserRating, name='cat1') is category1_new
        True
        >>> gsm.adapters.lookup((IDynamicType,), IUserRating, name='cat1') is category1
        True
        >>> sm.adapters.lookup((IDynamicType,), IUserRating, name='cat2') is None
        True

    Note that in addition to overriding a global category, we have
    removed a local one.

    Though category1 is now in both the local and global site manager,
    it no longer appears in acquired_categories, because it has been
    shadowed by the local version and will never be used within the
    site.  But if we were to remove it from the local configuration the
    global configuration would b ecome effective again::

        >>> manager.acquired_categories
        []
        
        >>> manager.local_categories = [category3, category2]
        >>> len(manager.acquired_categories)
        1
        >>> manager.acquired_categories[0] is category1
        True
        >>> sm.adapters.lookup((IDynamicType,), IUserRating, name='cat1') is category1
        True

    The `local_categories` and `acquired_categories` attributes always present
    their contained categories in order::

        >>> category3.order = 500
        >>> category2.order = 200
        >>> manager.local_categories[0] is category2
        True
        >>> category3.order = 100
        >>> manager.local_categories[0] is category3
        True
        >>> category4 = RatingsCategoryFactory('category4', order=500)
        >>> 
        >>> ztapi.provideAdapter((IDynamicType,), IUserRating,
        ...                      category4)
        >>> manager.acquired_categories[0] is category1
        True
        >>> category4.order = 50
        >>> manager.acquired_categories[0] is category4
        True
        

    """
    
    implements(ICategoryContainer)
    adapts(ISite)
    
    def __init__(self, context):
        self.context = context
        self.sm = getSiteManager(context)
        self.nsm = queryNextSiteManager(context)
    
    def add(self, category):
        "add a new rating category to the local Site Manager"
        self.sm.registerAdapter(category, 
                                (IDynamicType,), 
                                IUserRating,
                                name=category.name or u'')
        
    def remove(self, category):
        """remove the given rating category from the local Site Manager"""
        assert category.name in [c.name for c in self.local_categories]
        self.sm.unregisterAdapter(category,
                                  (IDynamicType,),
                                  IUserRating,
                                  name=category.name)

    def modify(self, category):
        """modify the given rating category in the local Site Manager"""
        assert category.name in [c.name for c in self.local_categories]
        orig_category = self.sm.adapters.lookup((IDynamicType,),
                                                 IUserRating,
                                                 name=category.name)
        for name, field in getFieldsInOrder(IRatingCategory):
            if not field.readonly:
                setattr(orig_category, name, getattr(category, name))

    def _filter_categories(self, local):
        """separate categories in local and acquired one"""
        all_categories = self.sm.adapters.lookupAll((IDynamicType,),
                                                    IUserRating)
        parent_categories = {}
        if self.nsm is not None:
            for n, c in self.nsm.adapters.lookupAll((IDynamicType,),
                                                     IUserRating):
                parent_categories[id(c)] = c
        # use 'id' to check if these are the object exists here and in parent
        if local:
            filtered_categories = (c for n,c in all_categories if id(c)
                                                      not in parent_categories)
        else:
            filtered_categories = (c for n,c in all_categories if id(c)
                                                      in parent_categories)

        return filtered_categories

    def _get_acquired_categories(self):
        "gets registered rating categories acquired from site managers other then local one"

        return sorted(self._filter_categories(local=False), 
                       key=lambda x: x.order)
                
    def _get_local_categories(self):
        "gets the local site manager registered rating categories"
        
        return sorted(self._filter_categories(local=True), 
                       key=lambda x: x.order)
    
    
    def _set_categories(self, categories):
        """modifies the registered rating categories 
        to match the given list of categories"""
        orig_categories = self._get_local_categories()
        orig_names = dict((c.name,c) for c in orig_categories)
        for cat in categories:
            cat.name = cat.name or u''
            cat.order = cat.order is None and 100 or cat.order
            if cat.name == u'':
                prefix = name = queryUtility(IURLNormalizer).normalize(cat.title)
                i = 1
                while name in orig_names:
                    name = "%s_%s" % (prefix, i)
                    i += 1
                cat.name = name
                
        new_names = dict((c.name,c) for c in categories)
        
        for c in orig_categories:
            if c.name not in new_names:
                self.remove(c)
        
        for c in categories:
            if c.name not in orig_names:
                self.add(c)
            else:
                self.modify(c)
            
                
    local_categories = property(_get_local_categories, _set_categories)
    acquired_categories = property(_get_acquired_categories)

class ObjectDisplayWidget(ObjectWidget):
    """an object widget which hide all readonly attributes """

    template = ViewPageTemplateFile('display_object.pt')
    
    def __call__(self):
        return self.template()


class HiddenReadonlyObjectWidget(ObjectWidget):
    """an object widget which hide all readonly attributes """
    
    template = ViewPageTemplateFile('hidden_readonly_object.pt')
    
    def __call__(self):
        return self.template()

hr_category_widget = CustomWidgetFactory(HiddenReadonlyObjectWidget, RatingsCategoryFactory)
hr_categories_widget = CustomWidgetFactory(ListSequenceWidget, hr_category_widget)


display_category_widget = CustomWidgetFactory(ObjectDisplayWidget, RatingsCategoryFactory)
display_categories_widget = CustomWidgetFactory(SequenceDisplayWidget, display_category_widget)
