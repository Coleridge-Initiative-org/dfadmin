import graphene
import data_facility_admin.schema
from graphene_django.debug import DjangoDebug


class Query(data_facility_admin.schema.Query,
            graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='__debug')


schema = graphene.Schema(query=Query)
