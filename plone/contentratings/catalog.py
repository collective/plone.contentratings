# zope imports
from zope.component.interfaces import ComponentLookupError

from plone.indexer import indexer
from Products.CMFCore.interfaces import IDynamicType

from contentratings.interfaces import IUserRating

@indexer(IDynamicType)
def average_rating(object):
    """Returns a tuple of the average rating and number of ratings for
    easy sorting"""
    try:
        adapter = IUserRating(object)
        return (adapter.averageRating, adapter.numberOfRatings)
    except (ComponentLookupError, TypeError, ValueError):
        raise AttributeError

@indexer(IDynamicType)
def rating_users(object):
    try:
        return IUserRating(object).all_raters()
    except (ComponentLookupError, TypeError, ValueError):
        raise AttributeError

def index_on_rate(obj, event):
    obj.reindexObject(['average_rating', 'amount_of_ratings', 'rating_users'])
