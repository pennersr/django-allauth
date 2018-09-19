import graphene


class UsernameLoginInputType(graphene.InputObjectType):
    username = graphene.String()
    password = graphene.String()


class EmailLoginInputType(graphene.InputObjectType):
    email = graphene.String()
    password = graphene.String()
