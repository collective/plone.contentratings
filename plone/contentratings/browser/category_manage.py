from zope.interface import implements, alsoProvides
from zope.component import adapts, getSiteManager, queryUtility
from zope.app.form import CustomWidgetFactory
from zope.app.form.interfaces import MissingInputError
from zope.app.form.browser import ObjectWidget, ListSequenceWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.schema import getFieldsInOrder


from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.contentratings.browser.interfaces import ICategoryContainer, ITTWCategory
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
    
    def add(self, category):
        "add a new rating category to the local Site Manager"
        alsoProvides(category, ITTWCategory)
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
                
    def _get_categories(self):
        "gets all the registered rating categories"
        
        categories = self.sm.adapters.lookupAll((IDynamicType,),
                                                IUserRating)
        return sorted((c for n,c in categories), key=lambda x: x.order)
    
    def _set_categories(self, categories):
        """modifies the registered rating categories 
        to match the given list of categories"""
        orig_categories = self._get_categories()
        orig_names = dict((c.name,c) for c in orig_categories)
        for cat in categories:
            cat.name = cat.name or u''
            cat.order = cat.order is None and 100 or cat.order
            if cat.name == u'__new':
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
            elif ITTWCategory.providedBy(orig_names[c.name]):
                self.modify(c)
            
                
    categories = property(_get_categories, _set_categories)

class DisablingObjectWidget(ObjectWidget):
    """an object widget which hide all readonly attributes """

    template = ViewPageTemplateFile('disabling_object.pt')
    
    def __call__(self):
        return self.template()

    def setRenderedValue(self, value):
        """make sure we store the value on the widget"""
        self.value = value
        super(DisablingObjectWidget, self).setRenderedValue(value)

    def hidden(self):
        """Render the object as hidden fields."""
        result = []
        for name in self.names:
            result.append(self.getSubWidget(name).hidden())
        return "".join(result)
        
    def disabled(self):
        """Render a disabld version of the widget"""
        return self.template(disabled=True)
        
    def is_global(self):
        """decide if the interface ITTWCategory is implemented by given object"""
        return not ITTWCategory.providedBy(self.value)

class DisablingListSequenceWidget(ListSequenceWidget):
    """ a list widget which disables all entries not providing a specific interface"""
    
    template = ViewPageTemplateFile('disabling_sequence.pt')
    interface = ITTWCategory
    
    def is_enabled(self, value):
        """ decide if the interface is implemented by given object"""
        if value is not None:
            matching = [c for c in self.context.context.categories if c.name == value.name]
            if matching:
                return ITTWCategory.providedBy(matching[0])
        return True

    def getValuesAndWidgets(self):
        """Return a list of values and widgets to display"""
        sequence = self._getRenderedValue()
        result = []
        for i, value in enumerate(sequence):
            widget = self._getWidget(i)
            widget.setRenderedValue(value)
            result.append((value, widget))
        return result

category_widget = CustomWidgetFactory(DisablingObjectWidget, RatingsCategoryFactory)
categories_widget = CustomWidgetFactory(DisablingListSequenceWidget, category_widget)

