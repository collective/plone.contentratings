import unittest
from zope.testing import doctestunit
from zope.component import testing

from zope.schema.interfaces import IChoice, ISet
from zope.interface import Interface
from zope.app.testing import ztapi, setup
from zope.app.form.browser import ChoiceCollectionInputWidget
from zope.app.form.browser import MultiSelectSetWidget
from zope.app.form.browser import CollectionInputWidget
from zope.app.form.browser import DropdownWidget
from zope.app.form.browser import ChoiceInputWidget
from zope.app.form.interfaces import IInputWidget

def setUpBasicWidgets(test):
    testing.setUp(test)
    ztapi.provideAdapter((IChoice, Interface, Interface), IInputWidget,
                         DropdownWidget)
    ztapi.provideAdapter((IChoice, Interface), IInputWidget,
                         ChoiceInputWidget)
    ztapi.provideAdapter((ISet, IChoice, Interface), IInputWidget,
                         ChoiceCollectionInputWidget)
    ztapi.provideAdapter((ISet, Interface, Interface), IInputWidget,
                         MultiSelectSetWidget)
    ztapi.provideAdapter((ISet, Interface), IInputWidget,
                         CollectionInputWidget)

def setUpPlaceful(test):
    site = setup.placefulSetUp(True)
    test.globs = {'site': site}

def tearDownPlaceful(test):
    setup.placefulTearDown()

def test_suite():
    return unittest.TestSuite([

        # Unit tests
        doctestunit.DocTestSuite('plone.contentratings.browser.controlpanel',
                                 setUp=setUpBasicWidgets,
                                 tearDown=testing.tearDown,),
        doctestunit.DocTestSuite('plone.contentratings.browser.category_manage',
                                 setUp=setUpPlaceful,
                                 tearDown=tearDownPlaceful,),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
