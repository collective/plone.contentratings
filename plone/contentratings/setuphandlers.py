from plone.contentratings.browser.interfaces import ICategoryContainer
from zope.component.hooks import setSite


def uninstallVarious(context):
    """Remove all persistent configuration from the site manager"""
    if context.readDataFile('ratings-uninstall.txt') is None:
        return
    site = context.getSite()
    setSite(site)
    cat_manager = ICategoryContainer(site)
    for cat in cat_manager._get_local_categories():
        cat_manager.remove(cat)
