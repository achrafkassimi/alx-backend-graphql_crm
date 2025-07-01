import graphene
from crm.schema import CRMQuery  # Import your app's Query class

class Query(CRMQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)
