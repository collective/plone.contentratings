from zope.interface import alsoProvides, implements, noLongerProvides
from zope.component import adapts
from plone.directives import form

from zope.schema import Bool

from plone.contentratings.interfaces import _

from rwproperty import getproperty, setproperty

from plone.contentratings.interfaces import IDexterityRatingsEnabled

from plone.dexterity.interfaces import IDexterityContent


class IRatingBehavior(form.Schema):
    """ Allows enabling/disabling rating on individual items
    """
    form.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=('allow_ratings',),
    )
    
    allow_ratings = Bool(
             title=_(u'Enable ratings'),
             description=_(u'Enable ratings on this content item'),
             default=True
            )
                         
alsoProvides(IRatingBehavior, form.IFormFieldProvider)


class RatingBehavior(object):
    """ Store by applying a marker interface. This makes it easy to switch the view on and off.
    """
    
    implements(IRatingBehavior)
    adapts(IDexterityContent)
    
    def __init__(self, context):
        self.context = context

    @getproperty
    def allow_ratings(self):
        return IDexterityRatingsEnabled.providedBy(self.context)
        
    @setproperty
    def allow_ratings(self, value):
        if value == True:
            alsoProvides(self.context, IDexterityRatingsEnabled)
        else:
            noLongerProvides(self.context, IDexterityRatingsEnabled)
