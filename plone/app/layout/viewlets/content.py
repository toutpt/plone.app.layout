from Acquisition import aq_inner
from zope.component import getMultiAdapter
from plone.memoize.instance import memoize

from plone.app.layout.viewlets import ViewletBase

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName


class DocumentActionsViewlet(ViewletBase):
    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.portal_url = self.portal_state.portal_url()
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        plone_utils = getToolByName(aq_inner(self.context), 'plone_utils')
        self.getIconFor = plone_utils.getIconFor
        self.actions = self.context_state.actions().get('document_actions', None)

    render = ViewPageTemplateFile("document_actions.pt")


class DocumentBylineViewlet(ViewletBase):
    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.portal_url = self.portal_state.portal_url()
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        self.tools = getMultiAdapter((self.context, self.request),
                                     name='plone_tools')

    @memoize
    def show(self):
        properties = self.tools.properties()
        site_properties = getattr(properties, 'site_properties')
        anonymous = self.portal_state.anonymous()
        allowAnonymousViewAbout = site_properties.getProperty('allowAnonymousViewAbout', True)
        return not anonymous or allowAnonymousViewAbout

    @memoize
    def locked_icon(self):
        if self.context_state.is_locked():
            portal = self.portal_state.portal()
            icon = portal.restrictedTraverse('lock_icon.gif')
            return icon.tag(title='Locked')
        return ""

    @memoize
    def creator(self):
        return self.context.Creator()

    @memoize
    def author(self):
        membership = self.tools.membership()
        return membership.getMemberInfo(self.creator())

    @memoize
    def authorname(self):
        author = self.author()
        return author and author['fullname'] or self.creator()

    @memoize
    def isExpired(self):
        portal = self.portal_state.portal()
        return portal.restrictedTraverse('isExpired')(self.context)

    @memoize
    def toLocalizedTime(self, time, long_format=None):
        """Convert time to localized time
        """
        util = getToolByName(self.context, 'translation_service')
        return util.ulocalized_time(time, long_format, self.context,
                                    domain='plonelocales')

    render = ViewPageTemplateFile("document_byline.pt")
