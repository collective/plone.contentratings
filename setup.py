from setuptools import setup, find_packages
import sys, os
import xml.sax.saxutils

version = '0.1'

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    text = unicode(text, 'utf-8').encode('ascii', 'xmlcharrefreplace')
    return xml.sax.saxutils.escape(text)

description = read('README.txt') + '\n\n' + \
              'Detailed Documentation\n' + \
              '**********************\n\n' + \
              read('plone' , 'contentratings', 'README.txt')

setup(name='plone.contentratings',
      version=version,
      description="Plone support for the contentratings package",
      long_description="",
      classifiers=[
        'License :: OSI Approved :: GNU Public License (GPL)',
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone ratings',
      author='Alec Mitchell',
      author_email='apm13@columbia.edu',
      url='http://svn.plone.org/svn/collective/plone.contentratings',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'contentratings',
          'archetypes.schemaextender',
      ],
      )
