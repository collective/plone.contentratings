# zope imports
from zope.component.interfaces import ComponentLookupError

from plone.indexer import indexer
from Products.CMFCore.interfaces import IDynamicType

from contentratings.interfaces import IUserRating

@indexer(IDynamicType)
def average_rating(object):
    try:
        return IUserRating(object).averageRating
    except (ComponentLookupError, TypeError, ValueError):
        raise AttributeError

@indexer(IDynamicType)
def amount_of_ratings(object):
    try:
        return IUserRating(object).numberOfRatings
    except (ComponentLookupError, TypeError, ValueError):
        raise AttributeError
