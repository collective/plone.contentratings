import unittest
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.annotation.attribute import AttributeAnnotations
from zope.interface import directlyProvides
from zope.app.container.sample import SampleContainer
from zope.app.testing import ztapi
from zope.testing import doctestunit
from zope.component import testing

def setUpCategoryTests(test):
    testing.setUp(test)
    # Setup our adapter from category to rating api
    ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                         AttributeAnnotations)
    container = SampleContainer()
    directlyProvides(container, IAttributeAnnotatable)
    test.globs = {'my_container': container}

def test_suite():
    return unittest.TestSuite([

        # Unit tests
        doctestunit.DocFileSuite('assignment.txt',
                                 package='plone.contentratings',
                                 setUp=testing.setUp,
                                 tearDown=testing.tearDown),
        doctestunit.DocFileSuite('category.txt',
                                 package='plone.contentratings',
                                 setUp=setUpCategoryTests,
                                 tearDown=testing.tearDown),


        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
