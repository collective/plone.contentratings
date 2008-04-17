"""plone.contentratings Rating Category Assignment setup handlers.

$Id:$
"""

from sets import Set

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.app.component.hooks import getSite

from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects

from contentratings.interfaces import IRatingCategoryInfo
from plone.contentratings.interfaces import IRatingCategoryAssignment
from plone.contentratings.browser.interfaces import ICategoryContainer
from contentratings.category import RatingsCategoryFactory

_FILENAME = 'contentratings.xml'

class ContentRatingsXMLAdapter(XMLAdapterBase):
    """Mode in- and exporter for Rating Category Assignment.
    """

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node=self._doc.createElement('contentratings')
        node.appendChild(self._extractLocalCategories())
        node.appendChild(self._extractTypeAssignments())

        self._logger.info('Content Ratings type assignment and '
                          'local categories settings exported.')
        return node

    def _importNode(self, node):
        if self.environ.shouldPurge():
            self._purgeTypeRatingsSettings()

        self._initLocalCategoriesSettings(node)
        self._initTypeAssignmentsSettings(node)
        self._logger.info('contentratings: Type Ratings and assignment settings imported.')

    def _purgeTypeRatingsSettings(self):
        self.context._mapping.clear()
        category_container=ICategoryContainer(getSite())
        for cat in category_container.local_categories:
            category_container.remove(cat)
        
        
    def _initLocalCategoriesSettings(self, node):
        def _convert(type, value):
            if type=='string':
                return unicode(value)
            if type=='integer':
                return int(value)
            return value
            
        for child in node.childNodes:
            if child.nodeName=='categories':
                category_container=ICategoryContainer(getSite())
                current_categories=[cat.name for cat in 
                                        category_container._get_local_categories()]
                for category_node in child.getElementsByTagName('category'):
                    category_name=category_node.getAttribute('name')
                    attributes={'name': category_name}
                    for attr_node in category_node.getElementsByTagName('attr'):
                        attr_name = attr_node.getAttribute('name')
                        attr_type = attr_node.getAttribute('type')
                        attributes[str(attr_name)]=_convert(attr_type, 
                                                       attr_node.firstChild.data)
                    # XXX: should we always add or better to update already existing? 
                    # (should we purge at import?) 
                    if category_name in current_categories:
                        category_container.modify(RatingsCategoryFactory(**attributes))
                    else:
                        category_container.add(RatingsCategoryFactory(**attributes))
                        
    def _initTypeAssignmentsSettings(self, node):
        for child in node.childNodes:
            if child.nodeName=='assignments':
                for type_node in child.getElementsByTagName('type'):
                    portaltype=type_node.getAttribute('portal_type')
                    categories=[e.getAttribute('value') for e in
                                  type_node.getElementsByTagName('category')]
                    already = [cat.name for cat in
                                   self.context.categories_for_type(portaltype)]
                    categories=Set(categories + already)
                    self.context._mapping[portaltype] = categories
                

    def _extractTypeAssignments(self):
        node=self._doc.createElement('assignments')
        types_vocab = getUtility(IVocabularyFactory,
                                 'plone.contentratings.portal_types')(getSite())
        for portal_type in (el.token for el in types_vocab):
            type_categories = self.context.categories_for_type(portal_type)
            if type_categories:
                child=self._doc.createElement('type')
                child.setAttribute('portal_type', portal_type)
                for cat in type_categories:
                    sub=self._doc.createElement('category')
                    sub.setAttribute('value', cat.name)
                    child.appendChild(sub)
                node.appendChild(child)

        return node
        
    def _extractLocalCategories(self):
        node=self._doc.createElement('categories')
        attr_names=IRatingCategoryInfo.names()
        for category in ICategoryContainer(getSite())._get_local_categories():
            child=self._doc.createElement('category')
            child.setAttribute('name', category.name)
            for attr in attr_names:
                value=getattr(category, attr, None)
                if value is not None:
                    sub=self._doc.createElement('attr')
                    sub.setAttribute('name', attr)
                    if isinstance(attr, (str, unicode)):
                        sub.setAttribute('type', 'string')
                    if isinstance(attr, int):
                        sub.setAttribute('type', 'integer')
                    subchild = self._doc.createTextNode(unicode(value))
                    sub.appendChild(subchild)
                    child.appendChild(sub)
            node.appendChild(child)
        return node


def importTypeRatingAssignments(context):
    """Import Type Ratings Assignment configuration.
    """
    try:
        category_mng = getUtility(IRatingCategoryAssignment)
    except:
        category_mng = None
    if category_mng is None:
        logger = context.getLogger("contentratings")
        logger.info("plone.contentratings not installed in this portal.")
        return
        
    importObjects(category_mng, '', context)


def exportTypeRatingAssignments(context):
    """Export Type Ratings Assignment configuration.
    """
    category_mng = getUtility(IRatingCategoryAssignment)
    if category_mng is None:
        logger = context.getLogger("contentratings")
        logger.info("Nothing to export.")
        return

    exportObjects(category_mng, '', context)
