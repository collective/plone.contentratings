from zope.component import getMultiAdapter
from plone.app.layout.viewlets import ViewletBase

class UserRatingViewlet(ViewletBase):
    """A simple viewlet which renders the user and editorial rating
    aggregators"""

    def render(self):
        user = getMultiAdapter((self.context, self.request),
                               name='user-ratings')()
        editor = getMultiAdapter((self.context, self.request),
                                 name='editorial-ratings')()
        return '<div class="RatingViewlet">\n%s\n%s\n</div>'%(editor, user)
