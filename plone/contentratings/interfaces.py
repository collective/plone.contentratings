from zope.interface import Interface
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plone.contentratings')

class IRatingCategoryAssignment(Interface):

    def supports_category(content, category):
        """Returns True if the content object supports the given rating
        category"""

    def supported_categories(content):
        """Returns all categories supported by a given content object"""

    def assign_categories(portal_type, categories):
        """Sets the available categories for a given portal_type"""

    def categories_for_type(self, portal_type):
        """Gets all available categories for a given portal type"""

class IUnratable(Interface):
    """A marker interface indicating that an object is not ratable"""

