from zope.interface import implements, alsoProvides
from zope.component import adapts, getSiteManager, queryUtility
from zope.app.component import queryNextSiteManager
from zope.app.form import CustomWidgetFactory
from zope.app.form.interfaces import MissingInputError
from zope.app.form.browser import ObjectWidget, ListSequenceWidget, SequenceDisplayWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.schema import getFieldsInOrder


from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.contentratings.browser.interfaces import ICategoryContainer
from contentratings.interfaces import IUserRating
from contentratings.interfaces import IRatingCategory, _
from contentratings.category import RatingsCategoryFactory

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.interfaces import IDynamicType

class CategoryContainerAdapter(object):
    """ adapter for portal root to ICategoryContainer"""
    
    implements(ICategoryContainer)
    adapts(IPloneSiteRoot)
    
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
        self.sm.unregisterAdapter(category,
                                  (IDynamicType,),
                                  IUserRating,
                                  name=category.name)

    def modify(self, category):
        """modify the given rating category in the local Site Manager"""
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