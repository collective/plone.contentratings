from zope.interface import implements
from zope.component import adapts

from zope.app.component.hooks import getSite
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from plone.contentratings.interfaces import IRatingCategoryAssignment
from Products.CMFCore.utils import getToolByName

from plone.app.controlpanel.form import ControlPanelForm
from plone.fieldsets.fieldsets import FormFieldsets
from zope.app.form.browser.objectwidget import ObjectWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile 

from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.formlib import form

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.i18n import translate

from contentratings.interfaces import _

from plone.contentratings.browser.interfaces import IEditCategoryAssignment
from plone.contentratings.browser.interfaces import ICategoryAssignment
from plone.contentratings.interfaces import IRatingCategoryAssignment


from plone.app.kss.plonekssview import PloneKSSView
from kss.core import kssaction
from plone.app.kss.interfaces import IPloneKSSView



class CategoryAssignment(object):
    implements(ICategoryAssignment)


def types_vocab(context):
    """Types Vocabulary which doesn't freak out during validation"""
    context = getattr(context, 'context', context) or getSite()
    ptool = getToolByName(context, 'plone_utils', None)
    ttool = getToolByName(context, 'portal_types', None)
    if ptool is None or ttool is None:
        return None
    items = [ (ttool[t].Title(), t)
              for t in ptool.getUserFriendlyTypes() ]
    items.sort()
    items = [SimpleTerm(i[1], i[1], i[0]) for i in items]
    return SimpleVocabulary(items)


class AssignmentsAdapter(object):
    implements(IEditCategoryAssignment)
    adapts(IPloneSiteRoot)

    def __init__(self, context):
        self.context = context
        self.util = getUtility(IRatingCategoryAssignment)
        # need these for vocabulary lookup
        self.portal_types = getToolByName(context, 'portal_types')
        self.plone_utils = getToolByName(context, 'plone_utils')

    def _set_assignment(self, assignment):
        self.util.assign_categories(assignment.portal_type, 
                                    assignment.categories)

    def _get_assignment(self):
        return None
        # items = []
        # util = self.util
        # for ptype in util._mapping.keys():
        #     assignment = CategoryAssignment()
        #     assignment.portal_type = ptype
        #     assignment.categories = set(util.categories_for_type(ptype))
        #     items.append(assignment)
        # return tuple(items)

    assignment = property(fget=_get_assignment, fset=_set_assignment)

        

class AssignmentWidget(ObjectWidget):
    
    def __init__(self, context, request, **kw):
        super(AssignmentWidget, self).__init__(context, request, CategoryAssignment)
        
    def setRenderedValue(self, value=None):
        value = self.get_categories()
        super(AssignmentWidget, self).setRenderedValue(value)

 
    def get_categories(self):
        portal_type = self.request.form.get('type_id', 
                                            self.request.form.get('form.assignment.portal_type', None))
        if portal_type is None:
            vocab_factory = getUtility(IVocabularyFactory,
                                        name="plone.app.vocabularies.ReallyUserFriendlyTypes")
            portal_type = list(vocab_factory(self.context.context.context))[0].token
        
        assignment = CategoryAssignment()
        assignment.portal_type = portal_type
        assignment.categories = set(selected_categories(portal_type))
        
        return assignment
    
    
def selected_categories(portal_type):
    assignments = getUtility(IRatingCategoryAssignment)
    return (t for t in assignments.categories_for_type(portal_type))

    

typespolicies = FormFieldsets(IEditCategoryAssignment)

class ContentRatingsControlPanel(ControlPanelForm):
    
    form_name = _(u"Category Assignments")
    
    actions = ControlPanelForm.actions.copy()

    label = _(u"Set the categories for portal types")
    description = _(u"Settings related to content ratings.")
    
    typespolicies['assignment'].custom_widget = AssignmentWidget
    form_fields = FormFieldsets(typespolicies)
        
    @form.action(_(u'Change Portal Type'), name=u'change_type')
    def change_type(self, action, data):
        type_id = self.request.form['form.assignment.portal_type']
        self.request.form.clear()
        self.request.form['type_id'] = type_id
        return self()




class ControlPanelKSSView(PloneKSSView):
    """ kss change categories type """

    implements(IPloneKSSView)

    @kssaction
    def refresh_categories(self, type_id):
        
        field = IEditCategoryAssignment['assignment']
        adapted = IEditCategoryAssignment(self.context)
        field = field.bind(adapted)
        
        widget = AssignmentWidget(field, self.request)
        widget.setPrefix('form')
        widget.setRenderedValue()
        select = widget.getSubWidget('categories')
        html = select.renderValue(select._getFormValue())
        
        ksscore = self.getCommandSet('core')
        select = ksscore.getCssSelector('select[id=form.assignment.categories]')
        ksscore.replaceHTML(select, html)
        
