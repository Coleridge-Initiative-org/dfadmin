import graphene
from graphene_django.types import DjangoObjectType

from data_facility_admin.models import User, Project, ProjectMember

from graphene import relay, ObjectType
from graphene_django.filter import DjangoFilterConnectionField


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = ["ldap_id", "ldap_name"]
        interfaces = (relay.Node, )


class ProjectNode(DjangoObjectType):
    class Meta:
        model = Project
        filter_fields = {
            'ldap_id': ['exact'],
            'ldap_name': ['exact'],
        }
        interfaces = (relay.Node, )


class ProjectMemberNode(DjangoObjectType):
    class Meta:
        model = ProjectMember
        filter_fields = {
            'project': ['exact'],
            'project__ldap_name': ['exact'],
            'project__ldap_id': ['exact'],
            'member': ['exact'],
            'member__ldap_name': ['exact'],
            'member__ldap_id': ['exact'],
        }
        interfaces = (relay.Node, )


class Query(object):
    user = relay.Node.Field(UserNode)
    all_users = DjangoFilterConnectionField(UserNode)

    project = relay.Node.Field(ProjectNode)
    all_projects = DjangoFilterConnectionField(ProjectNode)

    project_member = relay.Node.Field(ProjectMemberNode)
    all_project_members = DjangoFilterConnectionField(ProjectMemberNode)
