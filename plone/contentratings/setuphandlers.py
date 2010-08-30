from zope.app.component.hooks import setSite
from zope.component import getSiteManager
from plone.contentratings.browser.interfaces import ICategoryContainer

def uninstallVarious(context):
    """Remove all persistent configuration from the site manager"""
    if context.readDataFile('ratings-uninstall.txt') is None:
        return
    site = context.getSite()
    setSite(site)
    sm = getSiteManager(site)
    cat_manager = ICategoryContainer(site)
    for cat in cat_manager._get_local_categories():
        cat_manager.remove(cat)
