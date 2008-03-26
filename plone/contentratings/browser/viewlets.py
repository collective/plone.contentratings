from zope.component import getMultiAdapter
from plone.app.layout.viewlets import ViewletBase

class UserRatingViewlet(ViewletBase):
    """A simple viewlet which renders the user rating aggregator"""

    def render(self):
        return getMultiAdapter((self.context, self.request),
                               name='user-ratings')()
