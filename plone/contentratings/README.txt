Using `plone.contentratings`
============================

After making the package `plone.contentratings` and its dependencies
available to your Zope instance and restarting Zope, you should have a
"product" called `contentratings` available in the Plone Quick
Installer (the `Add-on Products` control panel).  Installing this
"product" will add a new control panel to Plone called `Ratings`.
This panel provides two configuration sections.  One for associating
particular content types with rating categories, and another for
adding and managing rating categories.


Assigning Ratings
-----------------

On the `Rating Assignments` tab, you can choose a portal type and then
select the rating categories to associate with the type in the
multi-select below the type selector.  Once you have selected the
categories, press the save button before selecting another type.

Once this is done, a rating UI will appear on the view for the
selected type.  This ui will allow setting and viewing ratings in all
the selected categories.  The order in which the categories appear
will be the same as the order in the multi-select, and is determined
by the order specified in the rating category configuration (see the
next section).

You can disable ratings on an individual content object on the edit
form for that content object.  Just uncheck the `Enable Ratings`
checkbox on the `Settings` tab.


Managing Categories
-------------------

The `Manage Categories` tab of the control panel allows you to create
custom categories, and modify or remove categories that you have
created.  Initially, there will be no local categories, only `Acquired
Categories`.  These are categories which are not defined in the control
panel but in python packages/products on the filesystem.  The
acquired categories cannot be edited.

To add a new category, click the `Add Local Categories` button.  Then
fill in a title for the category (this is the title that will appear
in the rating UI).  All other fields are optional.  You may enter a
description (primarily for documentation purposes).  You can enter
TALES expressions for determining when users can and cannot view
or set ratings in the category.  If left blank all users will
be able to both view and set ratings.  To use permissions to
restrict the ratings, use an expression like::

  python: checkPermission('View', context)

The order in which the categories are displayed in the UI is
determined by the order attribute which should be an integer.  The
view setting determines how the rating should appear in the UI.
Python products can register rating views to provide different look
and feel or behavior.  Instructions for creating and registering new
views can be found in the documentation of the `contentratings`_
package.  If you use a completely custom class for your view, make
sure it implements the `contentratings.browser.interfaces.IRatingView`
interface and is registered for the
`contentratings.interfaces.IUserRating` interface, which will ensure
that it appears in the listing.

You can remove custom categories by checking the box next to the
category and clicking the remove button.  You can of course edit any
of the category attributes.  You must click the `Save` button to
record your changes (including removing categories).

**Notes On Category Names**: Internally, categories are registered
and accessed using unique names.  For TTW created categories, these
names are generated from the title using a mechanism similar to that
used by Plone to generate ids for content objects.  This has a couple
of consequences.  If you create a category, rate content using that
category, and then remove the category, the ratings will still be
stored on the content under the original category name.  So if
you later create a "new" category with the same title (and hence
the same name), all content previously rated under the category
will still have rating information attached.  This makes it very
easy to undo a mistaken removal of a category, but may cause some
unexpected behavior.

Additionally, this also makes it possible to override a category
defined globally by creating one with an identical name.  However,
there is no guarantee that the names of globally defined are related
to their titles, so it's not always obvious how to do this, nor is
aldoing this recommended.  You may end up with two categories with the
same title , differentiated only by their order, which is likely to
lead to confusion when assigning categories.


Advanced Topics
===============

Notes for Developers
--------------------

Creating global categories and custom rating views should be a
straightforward process for developers who have read the
`contentratings`_ documentation.  There are a few special things to
note when developing custom rating behavior for Plone.

If you want a custom global categories to be available in the control
panel, it must be registered for the
`Products.CMFCore.interfaces.IDynamicType` interface.  Also, only
categories providing the `contentratings.interfaces.IUserRating`
interface will appear in the control panel (which means that they must
use a storage factory implementing `IUserRating`).  If you register a
category for an interface specific to your type(s), then it will
appear in the UI on any content implementing that interface,
will not appear in the control panel configuration, and will not
respect the `Enable Ratings` checkbox on content objects.

If you want to implement a custom `Rating Manager` for your content
types (which presumably also implement IDynamicType), you should
inherit from the `PloneRatingCategoryAdapter`, rather than the
standard `RatingCategoryAdapter` in `contentratings`_.  Without the
behaviors defined in this class, any TTW categories assigned to types
using the custom rating manager are likely to break or not appear.


Local Configuration
-------------------

It's possible to install a `LocalAssignmentUtility` (from
`plone.contentratings.assignment`) in any local site manager within a
CMF site.  When this is done, the `@@contentratings-controlpanel` view
can be used on that local site.  When changes are made in the local
control panel, they will affect content within that local site.

Within a local site, the `Acquired Categories` section of the `Manage
Categories` tab will contain both global categories and categories
defined in site managers below the current site (e.g. at the portal).
These cannot be edited, but they can be overridden (see the
**Notes On Category Names** section above).

Installing the utility in a local site manager above the Plone root,
must be done programatically for now.  The promising `plone.localconf`
package may soon provide a generic mechanism and UI for such
installations.


.. _contentratings: http://pypi.python.org/pypi/contentratings/
