from plone.dexterity.interfaces import IDexterityContent
from rwproperty import getproperty, setproperty
from z3c.form.interfaces import IEditForm, IAddForm
from zope.component import adapts
from zope.interface import alsoProvides, implements, noLongerProvides
from zope.schema import Bool
try:
    from plone.supermodel.model import Schema, fieldset
    from plone.autoform.directives import omitted, no_omit
    from plone.autoform.interfaces import IFormFieldProvider
    Schema, fieldset, omitted, no_omit, IFormFieldProvider  # pyflakes
except ImportError:
    # BBB dexterity 1.x
    from plone.directives.form import (Schema, fieldset, omitted,
                                       no_omit, IFormFieldProvider,)

from plone.contentratings.interfaces import IDexterityRatingsEnabled
from plone.contentratings.interfaces import _


class IRatingBehavior(Schema):
    """ Allows enabling/disabling rating on individual items
    """
    fieldset('settings', label=_(u"Settings"),
             fields=['allow_ratings'])
    allow_ratings = Bool(
        title=_(u'Enable Ratings'),
        description=_(u'Enable ratings on this content item'),
        default=True
        )
    omitted('allow_ratings')
    no_omit(IEditForm, 'allow_ratings')
    no_omit(IAddForm, 'allow_ratings')

alsoProvides(IRatingBehavior, IFormFieldProvider)


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
        if value:
            alsoProvides(self.context, IDexterityRatingsEnabled)
        else:
            noLongerProvides(self.context, IDexterityRatingsEnabled)
