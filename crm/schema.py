import re

import graphene
from graphene import Decimal
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from decimal import Decimal as D
from crm.models import Customer, Order, Product
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
from crm.filters import CustomerFilter, ProductFilter, OrderFilter


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (relay.Node,)


class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone):
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists")
        if phone and not re.match(r'^(\+?\d{7,15}|\d{3}-\d{3}-\d{4})$', phone):
            raise Exception("Invalid phone format")
        customer = Customer(name=name, email=email, phone=phone or "")
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.JSONString, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created = []
        errors = []

        for i, data in enumerate(input):
            try:
                name = data.get("name")
                email = data.get("email")
                phone = data.get("phone", "")

                if not name or not email:
                    raise Exception(f"Missing required fields for record {i + 1}")
                if Customer.objects.filter(email=email).exists():
                    raise Exception(f"Email already exists: {email}")
                if phone and not re.match(r'^(\+?\d{7,15}|\d{3}-\d{3}-\d{4})$', phone):
                    raise Exception(f"Invalid phone format: {phone}")

                customer = Customer(name=name, email=email, phone=phone)
                customer.save()
                created.append(customer)

            except Exception as e:
                errors.append(str(e))

        return BulkCreateCustomers(customers=created, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = Decimal(required=True)
        stock = graphene.Int()

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise Exception("Price must be a positive value.")
        if stock < 0:
            raise Exception("Stock cannot be negative.")
        product = Product(name=name, price=D(price), stock=stock)
        product.save()
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime()

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        if not product_ids:
            raise Exception("At least one product must be selected")

        products = []
        total = 0
        for pid in product_ids:
            try:
                product = Product.objects.get(pk=pid)
                total += float(product.price)
                products.append(product)
            except Product.DoesNotExist:
                raise Exception(f"Invalid product ID: {pid}")

        order = Order(customer=customer, total_amount=total)
        if order_date:
            order.order_date = order_date
        order.save()
        order.products.set(products)
        return CreateOrder(order=order)


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType)
    all_orders = DjangoFilterConnectionField(OrderType)

    def resolve_all_customers(root, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        return qs.order_by(order_by) if order_by else qs

    def resolve_all_products(root, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        return qs.order_by(order_by) if order_by else qs

    def resolve_all_orders(root, info, order_by=None, **kwargs):
        qs = Order.objects.all()
        return qs.order_by(order_by) if order_by else qs
