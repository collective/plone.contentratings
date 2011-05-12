from setuptools import setup, find_packages
import sys, os
import xml.sax.saxutils
from xml.dom.minidom import parse

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    text = unicode(text, 'utf-8').encode('ascii', 'xmlcharrefreplace')
    return text

description = read('README.txt') + '\n\n' + \
              'Detailed Documentation\n' + \
              '**********************\n\n' + \
              read('plone' , 'contentratings', 'README.txt') + '\n\n' + \
              read('plone' , 'contentratings', 'TODO.txt') + '\n\n' + \
              read('docs', 'HISTORY.txt')

setup(name='plone.contentratings',
      version="1.0-rc3",
      description="Plone support for the contentratings package",
      long_description=description,
      classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
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
          'contentratings>=1.0-rc1',
          'archetypes.schemaextender',
      ],
      entry_points="""
[z3c.autoinclude.plugin]
target = plone
      """,
      )
