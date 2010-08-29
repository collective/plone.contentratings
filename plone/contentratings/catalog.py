# zope imports
from plone.indexer import indexer
from Products.CMFCore.interfaces import IDynamicType

from contentratings.interfaces import IUserRating
from contentratings.browser.aggregator import get_rating_categories

def _first_user_rating(object):
    categories = get_rating_categories(object, IUserRating)
    for adapter in categories:
        # Just return the values for the first one
        return adapter
    # If we find nothing, fail
    raise AttributeError

@indexer(IDynamicType)
def average_rating(object):
    """Returns a tuple of the average rating and number of ratings for
    easy sorting"""
    adapter = _first_user_rating(object)
    return (adapter.averageRating, adapter.numberOfRatings)

@indexer(IDynamicType)
def rating_users(object):
    return _first_user_rating(object).all_raters()

def index_on_rate(obj, event):
    obj.reindexObject(['average_rating', 'amount_of_ratings', 'rating_users'])
