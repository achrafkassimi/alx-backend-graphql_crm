import graphene
from graphene_django.types import DjangoObjectType
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
import re

from .models import Customer, Product, Order

class CRMQuery(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

def validate_phone(phone):
    if phone is None:
        return True
    pattern = r'^(\+\d{10,15}|(\d{3}-\d{3}-\d{4}))$'
    if not re.match(pattern, phone):
        raise ValidationError("Phone number format is invalid. Expected +1234567890 or 123-456-7890.")

class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists.")
        try:
            validate_phone(phone)
        except ValidationError as e:
            raise Exception(str(e))

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully.")

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        customers = []
        errors = []
        with transaction.atomic():
            for idx, cust_input in enumerate(input):
                try:
                    if Customer.objects.filter(email=cust_input.email).exists():
                        raise Exception(f"Email {cust_input.email} already exists.")
                    validate_phone(cust_input.phone)
                    customer = Customer(name=cust_input.name, email=cust_input.email, phone=cust_input.phone)
                    customer.save()
                    customers.append(customer)
                except Exception as e:
                    errors.append(f"Error for record {idx + 1}: {str(e)}")

        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int()

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise Exception("Price must be positive.")
        if stock < 0:
            raise Exception("Stock cannot be negative.")

        product = Product(name=name, price=price, stock=stock)
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
            raise Exception("Invalid customer ID.")

        if not product_ids:
            raise Exception("At least one product must be selected.")

        products = Product.objects.filter(pk__in=product_ids)
        if products.count() != len(product_ids):
            raise Exception("One or more product IDs are invalid.")

        if order_date is None:
            order_date = now()

        total_amount = sum([p.price for p in products])

        order = Order(customer=customer, total_amount=total_amount, order_date=order_date)
        order.save()
        order.products.set(products)
        order.save()

        return CreateOrder(order=order)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()
