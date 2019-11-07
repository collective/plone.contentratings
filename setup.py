import os

from setuptools import setup, find_packages


def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    text = unicode(text, 'utf-8').encode('ascii', 'xmlcharrefreplace')
    return text

tests_require = [
    'zope.testing',
    'zope.app.testing',
    'zope.container',
    ]

description = '\n\n'.join([
    read('README.txt'),
    ('Detailed Documentation\n'
     '**********************\n'),
    read('plone', 'contentratings', 'README.txt'),
    read('plone', 'contentratings', 'TODO.txt'),
    read('docs', 'HISTORY.txt'),
    ])

setup(name='plone.contentratings',
      version='1.2.0.dev0',
      description="Plone support for the contentratings package",
      long_description=description,
      classifiers=[
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Framework :: Plone",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Framework :: Zope2",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='plone ratings, dexterity, behaviour, behavior',
      author='Alec Mitchell',
      author_email='apm13@columbia.edu',
      url='https://github.com/collective/plone.contentratings',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          'Products.CMFCore',
          'Products.ATContentTypes',
          'Products.Archetypes',
          'archetypes.schemaextender',
          'contentratings>=1.0',
          'plone.app.controlpanel',
          'rwproperty',
          # Include this will break sauna.reload: failed to load zope.site
          # 'zope.app.component',
          'zope.app.form',
          'zope.browserpage',
          'zope.component',
          'plone.directives.form',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
