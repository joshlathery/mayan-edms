from __future__ import absolute_import, unicode_literals

from django.core.exceptions import PermissionDenied
from django.template import TemplateSyntaxError, Library, Node, Variable

from permissions.models import Permission

register = Library()


class CheckPermissionsNode(Node):
    def __init__(self, requester, permission_list=None, *args, **kwargs):
        self.requester = requester
        self.permission_list = permission_list

    def render(self, context):
        permission_list = Variable(self.permission_list).resolve(context)
        if not permission_list:
            # There is no permissions list to check against which means
            # this link is available for all
            context['permission'] = True
            return ''
        requester = Variable(self.requester).resolve(context)
        try:
            Permission.objects.check_permissions(requester, permission_list)
            context['permission'] = True
            return ''
        except PermissionDenied:
            context['permission'] = False
            return ''


@register.tag
def check_permissions(parser, token):
    try:
        # Splitting by None == splitting by spaces.
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise TemplateSyntaxError('%r tag requires arguments' % token.contents.split()[0])

    return CheckPermissionsNode(*args.split())
