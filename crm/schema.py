import graphene

class CRMQuery(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
